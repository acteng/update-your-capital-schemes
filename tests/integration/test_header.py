from typing import Any, Mapping

import pytest
from flask.testing import FlaskClient

from schemes.domain.authorities import Authority, AuthorityRepository
from schemes.domain.users import User, UserRepository
from tests.integration.pages import SchemesPage, StartPage


class TestHeaderWhenUnauthenticated:
    def test_home_shows_start(self, client: FlaskClient) -> None:
        start_page = StartPage.open(client)

        assert start_page.header.home_url == "/"


class TestHeaderWhenAuthenticated:
    @pytest.fixture(name="config", scope="class")
    def config_fixture(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        return dict(config) | {"GOVUK_PROFILE_URL": "https://example.com/profile"}

    @pytest.fixture(name="auth", autouse=True)
    def auth_fixture(self, authorities: AuthorityRepository, users: UserRepository, client: FlaskClient) -> None:
        authorities.add(Authority(id_=1, name="Liverpool City Region Combined Authority"))
        users.add(User(email="boardman@example.com", authority_id=1))
        with client.session_transaction() as session:
            session["user"] = {"email": "boardman@example.com"}

    def test_home_shows_start(self, client: FlaskClient) -> None:
        schemes_page = SchemesPage.open(client)

        assert schemes_page.header.home_url == "/"

    def test_profile_shows_profile(self, client: FlaskClient) -> None:
        schemes_page = SchemesPage.open(client)

        assert schemes_page.header.profile_url == "https://example.com/profile"

    def test_sign_out_signs_out(self, client: FlaskClient) -> None:
        schemes_page = SchemesPage.open(client)

        assert schemes_page.header.sign_out_url == "/auth/logout"