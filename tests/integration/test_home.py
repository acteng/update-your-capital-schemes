from typing import Any, Mapping

import pytest
from flask.testing import FlaskClient

from tests.integration.pages import HomePage


@pytest.fixture(name="config")
def config_fixture(config: Mapping[str, Any]) -> Mapping[str, Any]:
    return config | {"GOVUK_PROFILE_URL": "https://example.com/profile"}


@pytest.fixture(name="client")
def client_fixture(client: FlaskClient) -> FlaskClient:
    with client.session_transaction() as session:
        session["user"] = {"email": "boardman@example.com"}
    return client


def test_header_home_shows_start(client: FlaskClient) -> None:
    home_page = HomePage(client).open()

    assert home_page.header().home_url == "/"


def test_header_profile_shows_profile(client: FlaskClient) -> None:
    home_page = HomePage(client).open()

    assert home_page.header().profile_url == "https://example.com/profile"


def test_header_sign_out_signs_out(client: FlaskClient) -> None:
    home_page = HomePage(client).open()

    assert home_page.header().sign_out_url == "/auth/logout"


def test_home(client: FlaskClient) -> None:
    home_page = HomePage(client).open()

    assert home_page.visible()
