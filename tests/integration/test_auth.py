from typing import Any, Mapping
from unittest.mock import Mock

import pytest
from authlib.integrations.flask_client import OAuth
from authlib.oidc.core import UserInfo
from flask import current_app, session
from flask.testing import FlaskClient

from tests.integration.pages import UnauthorizedPage


@pytest.fixture(name="config")
def config_fixture(config: Mapping[str, Any]) -> Mapping[str, Any]:
    return config | {"GOVUK_END_SESSION_ENDPOINT": "https://example.com/logout"}


def test_callback_logs_in(client: FlaskClient) -> None:
    current_app.extensions["users"].append("boardman@example.com")
    _given_oidc_returns_token_response({"id_token": "jwt"})
    _given_oidc_returns_user_info(UserInfo({"email": "boardman@example.com"}))

    with client:
        client.get("/auth")

        assert session["user"] == UserInfo({"email": "boardman@example.com"}) and session["id_token"] == "jwt"


def test_callback_redirects_to_home(client: FlaskClient) -> None:
    current_app.extensions["users"].append("boardman@example.com")
    _given_oidc_returns_token_response({"id_token": "jwt"})
    _given_oidc_returns_user_info(UserInfo({"email": "boardman@example.com"}))

    response = client.get("/auth")

    assert response.status_code == 302 and response.location == "/home"


def test_callback_when_unauthorized_redirects_to_unauthorized(client: FlaskClient) -> None:
    current_app.extensions["users"].append("boardman@example.com")
    _given_oidc_returns_token_response({"id_token": "jwt"})
    _given_oidc_returns_user_info(UserInfo({"email": "obree@example.com"}))

    response = client.get("/auth")

    assert response.status_code == 302 and response.location == "/auth/unauthorized"


def test_unauthorized(client: FlaskClient) -> None:
    unauthorized_page = UnauthorizedPage(client).open()

    assert unauthorized_page.visible() and unauthorized_page.is_unauthorized()


def test_logout_logs_out_from_oidc(client: FlaskClient) -> None:
    with client.session_transaction() as setup_session:
        setup_session["user"] = UserInfo({"email": "boardman@example.com"})
        setup_session["id_token"] = "jwt"

    response = client.get("/auth/logout")

    assert (
        response.status_code == 302
        and response.location
        == "https://example.com/logout?id_token_hint=jwt&post_logout_redirect_uri=http%3A%2F%2Flocalhost%2F"
    )


def test_logout_logs_out_from_schemes(client: FlaskClient) -> None:
    with client.session_transaction() as setup_session:
        setup_session["user"] = UserInfo({"email": "boardman@example.com"})
        setup_session["id_token"] = "jwt"

    with client:
        client.get("/auth/logout")

        assert "user" not in session and "id_token" not in session


def _given_oidc_returns_token_response(token: dict[str, str]) -> None:
    _get_oauth().govuk.authorize_access_token = Mock(return_value=token)


def _given_oidc_returns_user_info(user_info: UserInfo) -> None:
    _get_oauth().govuk.userinfo = Mock(return_value=user_info)


def _get_oauth() -> OAuth:
    return current_app.extensions["authlib.integrations.flask_client"]