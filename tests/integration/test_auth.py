from datetime import datetime
from typing import Any, Generator, Mapping

import pytest
import responses
from authlib.integrations.base_client import OAuthError
from authlib.integrations.flask_client import OAuth
from authlib.jose.errors import (
    BadSignatureError,
    ExpiredTokenError,
    InvalidClaimError,
    InvalidTokenError,
)
from authlib.oidc.core import UserInfo
from flask import current_app, session
from flask.testing import FlaskClient
from requests import HTTPError

from schemes.domain.users import User, UserRepository
from tests.integration.oidc import StubOidcServer


class TestAuth:
    @pytest.fixture(name="client_id", scope="class")
    def client_id_fixture(self) -> str:
        return "stub_client_id"

    @pytest.fixture(name="config", scope="class")
    def config_fixture(self, config: Mapping[str, Any], client_id: str) -> Mapping[str, Any]:
        return dict(config) | {"GOVUK_CLIENT_ID": client_id, "GOVUK_END_SESSION_ENDPOINT": "https://example.com/logout"}

    @pytest.fixture(name="oauth")
    def oauth_fixture(self) -> Generator[OAuth, None, None]:
        oauth = current_app.extensions["authlib.integrations.flask_client"]
        oauth_app = oauth.govuk
        previous_server_metadata = oauth_app.server_metadata
        yield oauth
        oauth_app.server_metadata = previous_server_metadata

    @pytest.fixture(autouse=True)
    def stub_server_metadata(self, oauth: OAuth) -> None:
        oauth.govuk.server_metadata = {"_loaded_at": 1}

    @pytest.fixture(name="oidc_server")
    def oidc_server_fixture(self, client_id: str, oauth: OAuth) -> StubOidcServer:
        oidc_server = StubOidcServer(client_id=client_id)
        oauth.govuk.server_metadata["authorization_endpoint"] = "https://stub.example/authorize"
        oauth.govuk.server_metadata["token_endpoint"] = oidc_server.token_endpoint
        oauth.govuk.server_metadata["userinfo_endpoint"] = oidc_server.userinfo_endpoint
        oauth.govuk.server_metadata["jwks"] = oidc_server.key_set()
        return oidc_server

    def test_authorize_redirect_sets_secure_session_cookie(
        self, oidc_server: StubOidcServer, client: FlaskClient
    ) -> None:
        response = client.get("/schemes")

        cookie = response.headers["Set-Cookie"]
        assert cookie.startswith("session=") and "; Secure;" in cookie

    def test_authorize_redirect_sets_http_only_session_cookie(
        self, oidc_server: StubOidcServer, client: FlaskClient
    ) -> None:
        response = client.get("/schemes")

        cookie = response.headers["Set-Cookie"]
        assert cookie.startswith("session=") and "; HttpOnly;" in cookie

    @responses.activate
    def test_callback_logs_in(self, oidc_server: StubOidcServer, users: UserRepository, client: FlaskClient) -> None:
        users.add(User("boardman@example.com", authority_id=1))
        id_token = oidc_server.given_token_endpoint_returns_id_token(nonce="456")
        oidc_server.given_userinfo_endpoint_returns_claims(email="boardman@example.com")
        given_session_has_authentication_request(client, state="123", nonce="456")

        with client:
            client.get("/auth", query_string={"code": "x", "state": "123"})

            assert session["user"] == UserInfo({"email": "boardman@example.com"}) and session["id_token"] == id_token

    @responses.activate
    def test_callback_redirects_to_schemes(
        self, oidc_server: StubOidcServer, users: UserRepository, client: FlaskClient
    ) -> None:
        users.add(User("boardman@example.com", authority_id=1))
        oidc_server.given_token_endpoint_returns_id_token(nonce="456")
        oidc_server.given_userinfo_endpoint_returns_claims(email="boardman@example.com")
        given_session_has_authentication_request(client, state="123", nonce="456")

        response = client.get("/auth", query_string={"code": "x", "state": "123"})

        assert response.status_code == 302 and response.location == "/schemes"

    def test_callback_when_authentication_error_raises_error(self, client: FlaskClient) -> None:
        with pytest.raises(OAuthError, match="invalid_request: Unsupported response"):
            client.get("/auth", query_string={"error": "invalid_request", "error_description": "Unsupported response"})

    @responses.activate
    def test_callback_when_id_token_issuer_invalid_raises_error(
        self, oidc_server: StubOidcServer, oauth: OAuth, client: FlaskClient
    ) -> None:
        oidc_server.given_token_endpoint_returns_id_token(issuer="https://malicious.example/", nonce="456")
        oauth.govuk.server_metadata["issuer"] = "https://stub.example/"
        given_session_has_authentication_request(client, state="123", nonce="456")

        with pytest.raises(InvalidClaimError, match='invalid_claim: Invalid claim "iss"'):
            client.get("/auth", query_string={"code": "x", "state": "123"})

    @responses.activate
    def test_callback_when_id_token_audience_invalid_raises_error(
        self, oidc_server: StubOidcServer, client: FlaskClient
    ) -> None:
        oidc_server.given_token_endpoint_returns_id_token(audience="another_client_id", nonce="456")
        given_session_has_authentication_request(client, state="123", nonce="456")

        with pytest.raises(InvalidClaimError, match='invalid_claim: Invalid claim "aud"'):
            client.get("/auth", query_string={"code": "x", "state": "123"})

    @responses.activate
    def test_callback_when_id_token_nonce_invalid_raises_error(
        self, oidc_server: StubOidcServer, client: FlaskClient
    ) -> None:
        oidc_server.given_token_endpoint_returns_id_token(nonce="789")
        given_session_has_authentication_request(client, state="123", nonce="456")

        with pytest.raises(InvalidClaimError, match='invalid_claim: Invalid claim "nonce"'):
            client.get("/auth", query_string={"code": "x", "state": "123"})

    @responses.activate
    def test_callback_when_id_token_expired_raises_error(
        self, oidc_server: StubOidcServer, client: FlaskClient
    ) -> None:
        oidc_server.given_token_endpoint_returns_id_token(expiration_time=1, nonce="456")
        given_session_has_authentication_request(client, state="123", nonce="456")

        with pytest.raises(ExpiredTokenError, match="expired_token: The token is expired"):
            client.get("/auth", query_string={"code": "x", "state": "123"})

    @responses.activate
    def test_callback_when_id_token_issued_in_future_raises_error(
        self, oidc_server: StubOidcServer, client: FlaskClient
    ) -> None:
        oidc_server.given_token_endpoint_returns_id_token(issued_at=int(datetime(3000, 1, 1).timestamp()), nonce="456")
        given_session_has_authentication_request(client, state="123", nonce="456")

        with pytest.raises(
            InvalidTokenError, match="invalid_token: The token is not valid as it was issued in the future"
        ):
            client.get("/auth", query_string={"code": "x", "state": "123"})

    @responses.activate
    def test_callback_when_id_token_signature_invalid_raises_error(
        self, oidc_server: StubOidcServer, client: FlaskClient
    ) -> None:
        oidc_server.given_token_endpoint_returns_id_token(nonce="456", signature="invalid_signature".encode())
        given_session_has_authentication_request(client, state="123", nonce="456")

        with pytest.raises(BadSignatureError):
            client.get("/auth", query_string={"code": "x", "state": "123"})

    @responses.activate
    def test_callback_when_token_error_raises_error(self, oidc_server: StubOidcServer, client: FlaskClient) -> None:
        oidc_server.given_token_endpoint_returns_error(error="invalid_request", error_description="invalid scope")
        given_session_has_authentication_request(client, state="123", nonce="456")

        with pytest.raises(OAuthError, match="invalid_request: invalid scope"):
            client.get("/auth", query_string={"code": "x", "state": "123"})

    @responses.activate
    def test_callback_when_userinfo_error_raises_error(self, oidc_server: StubOidcServer, client: FlaskClient) -> None:
        oidc_server.given_token_endpoint_returns_id_token(nonce="456")
        oidc_server.given_userinfo_endpoint_returns_error(
            error="invalid_token", error_description="The Access Token expired"
        )
        given_session_has_authentication_request(client, state="123", nonce="456")

        with pytest.raises(HTTPError, match=f"401 Client Error: Unauthorized for url: {oidc_server.userinfo_endpoint}"):
            client.get("/auth", query_string={"code": "x", "state": "123"})

    @responses.activate
    def test_callback_when_unauthorized_returns_forbidden(
        self, oidc_server: StubOidcServer, users: UserRepository, client: FlaskClient
    ) -> None:
        users.add(User("boardman@example.com", authority_id=1))
        oidc_server.given_token_endpoint_returns_id_token(nonce="456")
        oidc_server.given_userinfo_endpoint_returns_claims(email="obree@example.com")
        given_session_has_authentication_request(client, state="123", nonce="456")

        response = client.get("/auth", query_string={"code": "x", "state": "123"})

        assert response.status_code == 403

    def test_logout_logs_out_from_oidc(self, client: FlaskClient) -> None:
        with client.session_transaction() as setup_session:
            setup_session["user"] = UserInfo({"email": "boardman@example.com"})
            setup_session["id_token"] = "jwt"

        response = client.get("/auth/logout")

        assert (
            response.status_code == 302
            and response.location
            == "https://example.com/logout?id_token_hint=jwt&post_logout_redirect_uri=http%3A%2F%2Flocalhost%2F"
        )

    def test_logout_logs_out_from_schemes(self, client: FlaskClient) -> None:
        with client.session_transaction() as setup_session:
            setup_session["user"] = UserInfo({"email": "boardman@example.com"})
            setup_session["id_token"] = "jwt"

        with client:
            client.get("/auth/logout")

            assert "user" not in session and "id_token" not in session


def given_session_has_authentication_request(client: FlaskClient, state: str, nonce: str) -> None:
    with client.session_transaction() as setup_session:
        setup_session[f"_state_govuk_{state}"] = {"data": {"nonce": nonce}}
