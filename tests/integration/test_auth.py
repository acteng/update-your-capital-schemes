from typing import Any, Mapping

import pytest
from flask import session
from flask.testing import FlaskClient


@pytest.fixture(name="config")
def config_fixture(config: Mapping[str, Any]) -> Mapping[str, Any]:
    return config | {"GOVUK_END_SESSION_ENDPOINT": "https://example.com/logout"}


def test_logout_logs_out_from_oidc(client: FlaskClient) -> None:
    with client.session_transaction() as setup_session:
        setup_session["user"] = "test"
        setup_session["id_token"] = "id_token"

    response = client.get("/auth/logout")

    assert (
        response.status_code == 302
        and response.location
        == "https://example.com/logout?id_token_hint=id_token&post_logout_redirect_uri=http%3A%2F%2Flocalhost%2F"
    )


def test_logout_logs_out_from_schemes(client: FlaskClient) -> None:
    with client.session_transaction() as setup_session:
        setup_session["user"] = "test"
        setup_session["id_token"] = "test"

    with client:
        client.get("/auth/logout")

        assert "user" not in session and "id_token" not in session
