from typing import Any, Mapping
from unittest.mock import Mock

import pytest
from authlib.integrations.flask_client import OAuth
from authlib.oidc.core import UserInfo
from flask import current_app, session
from flask.testing import FlaskClient

from schemes.domain.users import User, UserRepository


class TestAuth:
    @pytest.fixture(name="config", scope="class")
    def config_fixture(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        return dict(config) | {"GOVUK_END_SESSION_ENDPOINT": "https://example.com/logout"}

    @pytest.fixture(name="oauth")
    def oauth_fixture(self) -> OAuth:
        return current_app.extensions["authlib.integrations.flask_client"]

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
