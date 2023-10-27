from typing import Any, Mapping

import inject
import pytest
from flask import Flask
from flask.testing import FlaskClient

from schemes.authorities import Authority, AuthorityRepository
from schemes.users import User, UserRepository
from tests.integration.pages import SchemesPage


@pytest.fixture(name="users")
def users_fixture(app: Flask) -> UserRepository:  # pylint: disable=unused-argument
    return inject.instance(UserRepository)


@pytest.fixture(name="authorities")
def authorities_fixture(app: Flask) -> AuthorityRepository:  # pylint: disable=unused-argument
    return inject.instance(AuthorityRepository)


@pytest.fixture(name="config")
def config_fixture(config: Mapping[str, Any]) -> Mapping[str, Any]:
    return config | {"GOVUK_PROFILE_URL": "https://example.com/profile"}


@pytest.fixture(name="auth", autouse=True)
def auth_fixture(authorities: AuthorityRepository, users: UserRepository, client: FlaskClient) -> None:
    authorities.add(Authority(id=1, name="Liverpool City Region Combined Authority"))
    users.add(User(email="boardman@example.com", authority_id=1))
    with client.session_transaction() as session:
        session["user"] = {"email": "boardman@example.com"}


def test_header_home_shows_start(client: FlaskClient) -> None:
    schemes_page = SchemesPage(client).open()

    assert schemes_page.header().home_url == "/"


def test_header_profile_shows_profile(client: FlaskClient) -> None:
    schemes_page = SchemesPage(client).open()

    assert schemes_page.header().profile_url == "https://example.com/profile"


def test_header_sign_out_signs_out(client: FlaskClient) -> None:
    schemes_page = SchemesPage(client).open()

    assert schemes_page.header().sign_out_url == "/auth/logout"


def test_schemes(client: FlaskClient) -> None:
    schemes_page = SchemesPage(client).open()

    assert schemes_page.authority() == "Liverpool City Region Combined Authority"
