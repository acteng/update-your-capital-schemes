from typing import Any, Generator, Mapping
from unittest.mock import Mock

import pytest
from authlib.integrations.base_client import OAuthError
from authlib.integrations.flask_client import OAuth
from authlib.jose.errors import InvalidClaimError
from authlib.oidc.core import UserInfo
from flask import current_app, session
from flask.testing import FlaskClient

from schemes.domain.users import User, UserRepository
from tests.integration.oidc import StubOAuth2Server


class TestAuth:
    @pytest.fixture(name="config", scope="class")
    def config_fixture(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        return dict(config) | {"GOVUK_END_SESSION_ENDPOINT": "https://example.com/logout"}

    @pytest.fixture(name="oauth")
    def oauth_fixture(self) -> Generator[OAuth, None, None]:
        oauth = current_app.extensions["authlib.integrations.flask_client"]
        oauth_app = oauth.govuk
        previous_server_metadata = oauth_app.server_metadata
        previous_client_cls = oauth_app.client_cls
        previous_authorize_access_token = oauth_app.authorize_access_token
        previous_userinfo = oauth_app.userinfo
        yield oauth
        oauth_app.server_metadata = previous_server_metadata
        oauth_app.client_cls = previous_client_cls
        oauth_app.authorize_access_token = previous_authorize_access_token
        oauth_app.userinfo = previous_userinfo

    @pytest.fixture(autouse=True)
    def stub_server_metadata(self, oauth: OAuth) -> None:
        oauth.govuk.server_metadata = {"_loaded_at": 1}

    def test_callback_logs_in(self, oauth: OAuth, users: UserRepository, client: FlaskClient) -> None:
        users.add(User("boardman@example.com", authority_id=1))
        oauth.govuk.authorize_access_token = Mock(return_value={"id_token": "jwt"})
        oauth.govuk.userinfo = Mock(return_value=UserInfo({"email": "boardman@example.com"}))

        with client:
            client.get("/auth")

            assert session["user"] == UserInfo({"email": "boardman@example.com"}) and session["id_token"] == "jwt"

    def test_callback_redirects_to_schemes(self, oauth: OAuth, users: UserRepository, client: FlaskClient) -> None:
        users.add(User("boardman@example.com", authority_id=1))
        oauth.govuk.authorize_access_token = Mock(return_value={"id_token": "jwt"})
        oauth.govuk.userinfo = Mock(return_value=(UserInfo({"email": "boardman@example.com"})))

        response = client.get("/auth")

        assert response.status_code == 302 and response.location == "/schemes"

    def test_callback_when_authentication_error_raises_error(self, users: UserRepository, client: FlaskClient) -> None:
        users.add(User("boardman@example.com", authority_id=1))

        with pytest.raises(OAuthError, match="invalid_request: Unsupported response"):
            client.get("/auth", query_string={"error": "invalid_request", "error_description": "Unsupported response"})

    def test_callback_when_invalid_issuer_raises_error(
        self, oauth: OAuth, users: UserRepository, client: FlaskClient
    ) -> None:
        users.add(User("boardman@example.com", authority_id=1))
        server = StubOAuth2Server()
        oauth.govuk.server_metadata["issuer"] = "https://stub.example/"
        oauth.govuk.server_metadata["jwks"] = server.key_set()
        oauth.govuk.client_cls = server.create_client_class(issuer="https://malicious.example/", nonce="456")
        with client.session_transaction() as setup_session:
            setup_session["_state_govuk_123"] = {"data": {"nonce": "456"}}

        with pytest.raises(InvalidClaimError, match='invalid_claim: Invalid claim "iss"'):
            client.get("/auth", query_string={"code": "x", "state": "123"})

    def test_callback_when_invalid_audience_raises_error(
        self, oauth: OAuth, users: UserRepository, client: FlaskClient
    ) -> None:
        users.add(User("boardman@example.com", authority_id=1))
        server = StubOAuth2Server()
        oauth.govuk.server_metadata["jwks"] = server.key_set()
        oauth.govuk.client_cls = server.create_client_class(audience="another_client_id", nonce="456")
        with client.session_transaction() as setup_session:
            setup_session["_state_govuk_123"] = {"data": {"nonce": "456"}}

        with pytest.raises(InvalidClaimError, match='invalid_claim: Invalid claim "aud"'):
            client.get("/auth", query_string={"code": "x", "state": "123"})

    def test_callback_when_unauthorized_returns_forbidden(
        self, oauth: OAuth, users: UserRepository, client: FlaskClient
    ) -> None:
        users.add(User("boardman@example.com", authority_id=1))
        oauth.govuk.authorize_access_token = Mock(return_value={"id_token": "jwt"})
        oauth.govuk.userinfo = Mock(return_value=(UserInfo({"email": "obree@example.com"})))

        response = client.get("/auth")

        assert response.status_code == 403

    def test_logout_logs_out_from_oidc(self, oauth: OAuth, client: FlaskClient) -> None:
        with client.session_transaction() as setup_session:
            setup_session["user"] = UserInfo({"email": "boardman@example.com"})
            setup_session["id_token"] = "jwt"

        response = client.get("/auth/logout")

        assert (
            response.status_code == 302
            and response.location
            == "https://example.com/logout?id_token_hint=jwt&post_logout_redirect_uri=http%3A%2F%2Flocalhost%2F"
        )

    def test_logout_logs_out_from_schemes(self, oauth: OAuth, client: FlaskClient) -> None:
        with client.session_transaction() as setup_session:
            setup_session["user"] = UserInfo({"email": "boardman@example.com"})
            setup_session["id_token"] = "jwt"

        with client:
            client.get("/auth/logout")

            assert "user" not in session and "id_token" not in session
