from dataclasses import dataclass

import pytest
import respx
from flask import Flask, request

from schemes.oauth import OAuthExtension
from tests.oauth import StubAuthorizationServer


@dataclass(frozen=True)
class _Client:
    client_id: str
    client_secret: str


@dataclass(frozen=True)
class _ResourceServer:
    url: str
    identifier: str


class TestOAuthExtension:
    @pytest.fixture(name="api_client")
    def api_client_fixture(self) -> _Client:
        return _Client(client_id="test", client_secret="secret")

    @pytest.fixture(name="api_server")
    def api_server_fixture(self) -> _ResourceServer:
        return _ResourceServer(url="https://api.example", identifier="https://api.example")

    @pytest.fixture(name="authorization_server")
    def authorization_server_fixture(self, api_server: _ResourceServer, api_client: _Client) -> StubAuthorizationServer:
        authorization_server = StubAuthorizationServer(
            api_server.identifier, api_client.client_id, api_client.client_secret
        )
        authorization_server.given_configuration_endpoint_returns_configuration()
        return authorization_server

    @pytest.fixture(name="app")
    def app_fixture(
        self, authorization_server: StubAuthorizationServer, api_client: _Client, api_server: _ResourceServer
    ) -> Flask:
        app = Flask("test")
        app.config.from_mapping(
            {
                "GOVUK_CLIENT_ID": "test",
                "GOVUK_CLIENT_SECRET": "test",
                "GOVUK_SERVER_METADATA_URL": "test",
                "GOVUK_TOKEN_ENDPOINT": "test",
                "ATE_CLIENT_ID": api_client.client_id,
                "ATE_CLIENT_SECRET": api_client.client_secret,
                "ATE_SERVER_METADATA_URL": authorization_server.configuration_endpoint,
                "ATE_AUDIENCE": api_server.identifier,
                "ATE_URL": api_server.url,
            }
        )
        return app

    @respx.mock
    async def test_ate_api_requests_access_token(
        self, app: Flask, authorization_server: StubAuthorizationServer, api_server: _ResourceServer
    ) -> None:
        oauth = OAuthExtension(app)
        authorization_server.given_token_endpoint_returns_access_token("dummy_jwt", expires_in=15 * 60)
        api_response = respx.get(api_server.url, headers={"Authorization": "Bearer dummy_jwt"})

        with app.app_context():
            await oauth.ate.request("GET", "/", request=request)

        assert api_response.call_count == 1

    @respx.mock
    async def test_ate_api_caches_access_token_within_request(
        self, app: Flask, authorization_server: StubAuthorizationServer, api_server: _ResourceServer
    ) -> None:
        oauth = OAuthExtension(app)
        token_response = authorization_server.given_token_endpoint_returns_access_token("dummy_jwt", expires_in=15 * 60)
        respx.get(api_server.url, headers={"Authorization": "Bearer dummy_jwt"})

        with app.app_context():
            await oauth.ate.request("GET", "/", request=request)
            await oauth.ate.request("GET", "/", request=request)

        assert token_response.call_count == 1

    @respx.mock
    async def test_ate_api_caches_access_token_across_requests(
        self, app: Flask, authorization_server: StubAuthorizationServer, api_server: _ResourceServer
    ) -> None:
        oauth = OAuthExtension(app)
        token_response = authorization_server.given_token_endpoint_returns_access_token("dummy_jwt", expires_in=15 * 60)
        respx.get(api_server.url, headers={"Authorization": "Bearer dummy_jwt"})

        with app.app_context():
            await oauth.ate.request("GET", "/", request=request)
        with app.app_context():
            await oauth.ate.request("GET", "/", request=request)

        assert token_response.call_count == 1

    @respx.mock
    async def test_ate_api_refreshes_access_token_when_expired(
        self, app: Flask, authorization_server: StubAuthorizationServer, api_server: _ResourceServer
    ) -> None:
        oauth = OAuthExtension(app)
        authorization_server.given_token_endpoint_returns_access_token("expired_jwt", expires_in=1 * 60)
        authorization_server.given_token_endpoint_returns_access_token("refreshed_jwt", expires_in=15 * 60)
        api_response = respx.get(api_server.url, headers={"Authorization": "Bearer refreshed_jwt"})

        with app.app_context():
            await oauth.ate.request("GET", "/", request=request)

        assert api_response.call_count == 1

    @respx.mock
    async def test_ate_api_uses_refreshed_access_token_across_requests(
        self, app: Flask, authorization_server: StubAuthorizationServer, api_server: _ResourceServer
    ) -> None:
        oauth = OAuthExtension(app)
        authorization_server.given_token_endpoint_returns_access_token("expired_jwt", expires_in=1 * 60)
        token_response = authorization_server.given_token_endpoint_returns_access_token(
            "refreshed_jwt", expires_in=15 * 60
        )
        api_response = respx.get(api_server.url, headers={"Authorization": "Bearer refreshed_jwt"})

        with app.app_context():
            await oauth.ate.request("GET", "/", request=request)
        with app.app_context():
            await oauth.ate.request("GET", "/", request=request)

        assert token_response.call_count == 2 and api_response.call_count == 2
