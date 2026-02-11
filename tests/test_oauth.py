from dataclasses import dataclass

import pytest
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat, PublicFormat
from flask import Flask, request
from httpx import Timeout
from respx import MockRouter

from schemes.oauth import OAuthExtension
from tests.oauth import StubAuthorizationServer


@dataclass(frozen=True)
class OAuthClient:
    client_id: str
    public_key: bytes


@dataclass(frozen=True)
class OAuthResourceServer:
    identifier: str


@dataclass(frozen=True)
class ApiServer:
    url: str


class TestOAuthExtension:
    @pytest.fixture(name="api_key_pair")
    def api_key_pair_fixture(self) -> RSAPrivateKey:
        return rsa.generate_private_key(backend=default_backend(), public_exponent=65537, key_size=2048)

    @pytest.fixture(name="api_private_key")
    def api_private_key_fixture(self, api_key_pair: RSAPrivateKey) -> bytes:
        return api_key_pair.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())

    @pytest.fixture(name="api_public_key")
    def api_public_key_fixture(self, api_key_pair: RSAPrivateKey) -> bytes:
        return api_key_pair.public_key().public_bytes(Encoding.OpenSSH, PublicFormat.OpenSSH)

    @pytest.fixture(name="api_oauth_client")
    def api_oauth_client_fixture(self, api_public_key: bytes) -> OAuthClient:
        return OAuthClient(client_id="test", public_key=api_public_key)

    @pytest.fixture(name="api_resource_server")
    def api_resource_server_fixture(self) -> OAuthResourceServer:
        return OAuthResourceServer(identifier="https://api.example")

    @pytest.fixture(name="api_server")
    def api_server_fixture(self) -> ApiServer:
        return ApiServer(url="https://api.example")

    @pytest.fixture(name="authorization_server")
    def authorization_server_fixture(
        self, respx_mock: MockRouter, api_resource_server: OAuthResourceServer, api_oauth_client: OAuthClient
    ) -> StubAuthorizationServer:
        authorization_server = StubAuthorizationServer(
            respx_mock, api_resource_server.identifier, api_oauth_client.client_id, api_oauth_client.public_key
        )
        authorization_server.given_configuration_endpoint_returns_configuration()
        return authorization_server

    @pytest.fixture(name="app")
    def app_fixture(
        self,
        authorization_server: StubAuthorizationServer,
        api_oauth_client: OAuthClient,
        api_private_key: bytes,
        api_resource_server: OAuthResourceServer,
        api_server: ApiServer,
    ) -> Flask:
        app = Flask("test")
        app.config.from_mapping(
            {
                "GOVUK_CLIENT_ID": "test",
                "GOVUK_CLIENT_SECRET": "test",
                "GOVUK_SERVER_METADATA_URL": "test",
                "ATE_CLIENT_ID": api_oauth_client.client_id,
                "ATE_CLIENT_SECRET": api_private_key.decode(),
                "ATE_SERVER_METADATA_URL": authorization_server.configuration_endpoint,
                "ATE_AUDIENCE": api_resource_server.identifier,
                "ATE_URL": api_server.url,
            }
        )
        return app

    def test_ate_api_uses_shorter_client_assertion_expiration_time(self, app: Flask) -> None:
        oauth = OAuthExtension(app)

        assert oauth.ate.client_kwargs.get("token_endpoint_auth_method").expires_in == 60

    def test_ate_api_uses_http2(self, app: Flask) -> None:
        oauth = OAuthExtension(app)

        assert oauth.ate.client_kwargs.get("http2")

    def test_ate_api_uses_longer_timeout(self, app: Flask) -> None:
        oauth = OAuthExtension(app)

        assert oauth.ate.client_kwargs.get("timeout") == Timeout(10)

    async def test_ate_api_uses_compression(
        self,
        respx_mock: MockRouter,
        app: Flask,
        authorization_server: StubAuthorizationServer,
        api_server: ApiServer,
    ) -> None:
        oauth = OAuthExtension(app)
        authorization_server.given_token_endpoint_returns_access_token("dummy_jwt", expires_in=15 * 60)
        api_response = respx_mock.get(api_server.url)

        with app.app_context():
            await oauth.ate.get("/", request=request)

        accept_encoding = api_response.calls.last.request.headers["Accept-Encoding"]
        assert "gzip" in [encoding.strip() for encoding in accept_encoding.split(",")]

    async def test_ate_api_requests_access_token(
        self,
        respx_mock: MockRouter,
        app: Flask,
        authorization_server: StubAuthorizationServer,
        api_server: ApiServer,
    ) -> None:
        oauth = OAuthExtension(app)
        authorization_server.given_token_endpoint_returns_access_token("dummy_jwt", expires_in=15 * 60)
        api_response = respx_mock.get(api_server.url, headers={"Authorization": "Bearer dummy_jwt"})

        with app.app_context():
            await oauth.ate.get("/", request=request)

        assert api_response.call_count == 1

    async def test_ate_api_caches_access_token_within_request(
        self,
        respx_mock: MockRouter,
        app: Flask,
        authorization_server: StubAuthorizationServer,
        api_server: ApiServer,
    ) -> None:
        oauth = OAuthExtension(app)
        token_response = authorization_server.given_token_endpoint_returns_access_token("dummy_jwt", expires_in=15 * 60)
        respx_mock.get(api_server.url, headers={"Authorization": "Bearer dummy_jwt"})

        with app.app_context():
            await oauth.ate.get("/", request=request)
            await oauth.ate.get("/", request=request)

        assert token_response.call_count == 1

    async def test_ate_api_caches_access_token_across_requests(
        self,
        respx_mock: MockRouter,
        app: Flask,
        authorization_server: StubAuthorizationServer,
        api_server: ApiServer,
    ) -> None:
        oauth = OAuthExtension(app)
        token_response = authorization_server.given_token_endpoint_returns_access_token("dummy_jwt", expires_in=15 * 60)
        respx_mock.get(api_server.url, headers={"Authorization": "Bearer dummy_jwt"})

        with app.app_context():
            await oauth.ate.get("/", request=request)
        with app.app_context():
            await oauth.ate.get("/", request=request)

        assert token_response.call_count == 1

    async def test_ate_api_refreshes_access_token_when_expired(
        self,
        respx_mock: MockRouter,
        app: Flask,
        authorization_server: StubAuthorizationServer,
        api_server: ApiServer,
    ) -> None:
        oauth = OAuthExtension(app)
        authorization_server.given_token_endpoint_returns_access_token("expired_jwt", expires_in=1 * 60)
        authorization_server.given_token_endpoint_returns_access_token("refreshed_jwt", expires_in=15 * 60)
        api_response = respx_mock.get(api_server.url, headers={"Authorization": "Bearer refreshed_jwt"})

        with app.app_context():
            await oauth.ate.get("/", request=request)

        assert api_response.call_count == 1

    async def test_ate_api_uses_refreshed_access_token_across_requests(
        self,
        respx_mock: MockRouter,
        app: Flask,
        authorization_server: StubAuthorizationServer,
        api_server: ApiServer,
    ) -> None:
        oauth = OAuthExtension(app)
        authorization_server.given_token_endpoint_returns_access_token("expired_jwt", expires_in=1 * 60)
        token_response = authorization_server.given_token_endpoint_returns_access_token(
            "refreshed_jwt", expires_in=15 * 60
        )
        api_response = respx_mock.get(api_server.url, headers={"Authorization": "Bearer refreshed_jwt"})

        with app.app_context():
            await oauth.ate.get("/", request=request)
        with app.app_context():
            await oauth.ate.get("/", request=request)

        assert token_response.call_count == 2 and api_response.call_count == 2
