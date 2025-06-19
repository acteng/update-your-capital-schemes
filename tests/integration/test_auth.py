import logging
from datetime import datetime
from typing import Any, Generator, Mapping

import pytest
import responses
from authlib.integrations.base_client import OAuthError
from authlib.integrations.flask_client import OAuth
from authlib.jose.errors import BadSignatureError, ExpiredTokenError, InvalidClaimError, InvalidTokenError
from authlib.oidc.core import UserInfo
from flask import current_app, session
from flask.testing import FlaskClient
from pytest import LogCaptureFixture
from requests import HTTPError

from schemes.domain.users import User, UserRepository
from tests.integration.oidc import StubOidcServer
from tests.integration.pages import BadRequestPage, ForbiddenPage


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

        value = response.headers["Set-Cookie"].split("; ")
        assert value[0].startswith("session=") and "Secure" in value

    def test_authorize_redirect_sets_http_only_session_cookie(
        self, oidc_server: StubOidcServer, client: FlaskClient
    ) -> None:
        response = client.get("/schemes")

        value = response.headers["Set-Cookie"].split("; ")
        assert value[0].startswith("session=") and "HttpOnly" in value

    def test_authorize_redirect_sets_same_site_session_cookie(
        self, oidc_server: StubOidcServer, client: FlaskClient
    ) -> None:
        response = client.get("/schemes")

        value = response.headers["Set-Cookie"].split("; ")
        assert value[0].startswith("session=") and "SameSite=Lax" in value

    @responses.activate
    def test_callback_logs_in(self, oidc_server: StubOidcServer, users: UserRepository, client: FlaskClient) -> None:
        users.add(User("boardman@example.com", authority_abbreviation="LIV"))
        id_token = oidc_server.given_token_endpoint_returns_id_token(nonce="456")
        oidc_server.given_userinfo_endpoint_returns_claims(email="boardman@example.com")
        given_session_has_authentication_request(client, state="123", nonce="456")

        with client:
            client.get("/auth", query_string={"code": "x", "state": "123"})

            assert session["user"] == UserInfo({"email": "boardman@example.com"}) and session["id_token"] == id_token

    @responses.activate
    def test_callback_logs_successful_sign_in(
        self, oidc_server: StubOidcServer, users: UserRepository, client: FlaskClient, caplog: LogCaptureFixture
    ) -> None:
        users.add(User("boardman@example.com", authority_abbreviation="LIV"))
        oidc_server.given_token_endpoint_returns_id_token(nonce="456")
        oidc_server.given_userinfo_endpoint_returns_claims(email="boardman@example.com")
        given_session_has_authentication_request(client, state="123", nonce="456")

        with client, caplog.at_level(logging.INFO):
            client.get("/auth", query_string={"code": "x", "state": "123"})

        assert (
            caplog.records[0].levelname == "INFO"
            and caplog.records[0].message == "User 'boardman@example.com' successfully signed in"
        )

    @responses.activate
    def test_callback_redirects_to_schemes(
        self, oidc_server: StubOidcServer, users: UserRepository, client: FlaskClient
    ) -> None:
        users.add(User("boardman@example.com", authority_abbreviation="LIV"))
        oidc_server.given_token_endpoint_returns_id_token(nonce="456")
        oidc_server.given_userinfo_endpoint_returns_claims(email="boardman@example.com")
        given_session_has_authentication_request(client, state="123", nonce="456")

        response = client.get("/auth", query_string={"code": "x", "state": "123"})

        assert response.status_code == 302 and response.location == "/schemes"

    @responses.activate
    def test_callback_when_authenticated_redirects_to_schemes(
        self, oidc_server: StubOidcServer, client: FlaskClient
    ) -> None:
        with client.session_transaction() as setup_session:
            setup_session["user"] = UserInfo({"email": "boardman@example.com"})
            setup_session["id_token"] = "jwt"

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

        with pytest.raises(InvalidClaimError, match="invalid_claim: Invalid claim 'iss'"):
            client.get("/auth", query_string={"code": "x", "state": "123"})

    @responses.activate
    def test_callback_when_id_token_audience_invalid_raises_error(
        self, oidc_server: StubOidcServer, client: FlaskClient
    ) -> None:
        oidc_server.given_token_endpoint_returns_id_token(audience="another_client_id", nonce="456")
        given_session_has_authentication_request(client, state="123", nonce="456")

        with pytest.raises(InvalidClaimError, match="invalid_claim: Invalid claim 'aud'"):
            client.get("/auth", query_string={"code": "x", "state": "123"})

    @responses.activate
    def test_callback_when_id_token_nonce_invalid_raises_error(
        self, oidc_server: StubOidcServer, client: FlaskClient
    ) -> None:
        oidc_server.given_token_endpoint_returns_id_token(nonce="789")
        given_session_has_authentication_request(client, state="123", nonce="456")

        with pytest.raises(InvalidClaimError, match="invalid_claim: Invalid claim 'nonce'"):
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
    def test_callback_when_unauthorized_logs_unauthorized_sign_in(
        self, oidc_server: StubOidcServer, users: UserRepository, client: FlaskClient, caplog: LogCaptureFixture
    ) -> None:
        users.add(User("boardman@example.com", authority_abbreviation="LIV"))
        oidc_server.given_token_endpoint_returns_id_token(nonce="456")
        oidc_server.given_userinfo_endpoint_returns_claims(email="obree@example.com")
        given_session_has_authentication_request(client, state="123", nonce="456")

        client.get("/auth", query_string={"code": "x", "state": "123"})

        assert (
            caplog.records[0].levelname == "WARNING"
            and caplog.records[0].message == "User 'obree@example.com' unauthorized sign in attempt"
        )

    @responses.activate
    def test_callback_when_unauthorized_redirects_to_forbidden(
        self, oidc_server: StubOidcServer, users: UserRepository, client: FlaskClient
    ) -> None:
        users.add(User("boardman@example.com", authority_abbreviation="LIV"))
        oidc_server.given_token_endpoint_returns_id_token(nonce="456")
        oidc_server.given_userinfo_endpoint_returns_claims(email="obree@example.com")
        given_session_has_authentication_request(client, state="123", nonce="456")

        response = client.get("/auth", query_string={"code": "x", "state": "123"})

        assert response.status_code == 302 and response.location == "/auth/forbidden"

    @responses.activate
    def test_callback_without_state_returns_bad_request(
        self, oidc_server: StubOidcServer, users: UserRepository, client: FlaskClient
    ) -> None:
        bad_request = BadRequestPage(client.get("/auth", query_string={"code": "x"}))

        assert bad_request.is_visible and bad_request.is_bad_request

    @responses.activate
    def test_callback_without_code_returns_bad_request(
        self, oidc_server: StubOidcServer, users: UserRepository, client: FlaskClient
    ) -> None:
        given_session_has_authentication_request(client, state="123", nonce="456")

        bad_request = BadRequestPage(client.get("/auth", query_string={"state": "123"}))

        assert bad_request.is_visible and bad_request.is_bad_request

    def test_forbidden(self, client: FlaskClient) -> None:
        forbidden_page = ForbiddenPage.open(client)

        assert forbidden_page.is_visible and forbidden_page.is_forbidden

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

    def test_logout_logs_sign_out(self, client: FlaskClient, caplog: LogCaptureFixture) -> None:
        with client.session_transaction() as setup_session:
            setup_session["user"] = UserInfo({"email": "boardman@example.com"})
            setup_session["id_token"] = "jwt"

        with caplog.at_level(logging.INFO):
            client.get("/auth/logout")

        assert (
            caplog.records[0].levelname == "INFO"
            and caplog.records[0].message == "User 'boardman@example.com' signed out"
        )

    def test_logout_logs_out_from_schemes(self, client: FlaskClient) -> None:
        with client.session_transaction() as setup_session:
            setup_session["user"] = UserInfo({"email": "boardman@example.com"})
            setup_session["id_token"] = "jwt"

        with client:
            client.get("/auth/logout")

            assert "user" not in session and "id_token" not in session

    def test_logout_when_unauthenticated_logs_out_from_oidc(self, client: FlaskClient) -> None:
        response = client.get("/auth/logout")

        assert response.status_code == 302 and response.location == "https://example.com/logout"

    def test_logout_when_unauthenticated_logs_sign_out(self, client: FlaskClient, caplog: LogCaptureFixture) -> None:
        with caplog.at_level(logging.INFO):
            client.get("/auth/logout")

        assert caplog.records[0].levelname == "INFO" and caplog.records[0].message == "User signed out"


def given_session_has_authentication_request(client: FlaskClient, state: str, nonce: str) -> None:
    with client.session_transaction() as setup_session:
        setup_session[f"_state_govuk_{state}"] = {"data": {"nonce": nonce}}
