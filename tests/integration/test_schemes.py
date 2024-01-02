from typing import Any, Mapping

import pytest
from flask.testing import FlaskClient

from schemes.domain.authorities import Authority, AuthorityRepository
from schemes.domain.schemes import FundingProgramme, Scheme, SchemeRepository
from schemes.domain.users import User, UserRepository
from tests.integration.pages import SchemesPage


@pytest.fixture(name="config")
def config_fixture(config: Mapping[str, Any]) -> Mapping[str, Any]:
    return dict(config) | {"GOVUK_PROFILE_URL": "https://example.com/profile"}


@pytest.fixture(name="auth", autouse=True)
def auth_fixture(authorities: AuthorityRepository, users: UserRepository, client: FlaskClient) -> None:
    authorities.add(Authority(id_=1, name="Liverpool City Region Combined Authority"))
    users.add(User(email="boardman@example.com", authority_id=1))
    with client.session_transaction() as session:
        session["user"] = {"email": "boardman@example.com"}


def test_header_home_shows_start(client: FlaskClient) -> None:
    schemes_page = SchemesPage.open(client)

    assert schemes_page.header.home_url == "/"


def test_header_profile_shows_profile(client: FlaskClient) -> None:
    schemes_page = SchemesPage.open(client)

    assert schemes_page.header.profile_url == "https://example.com/profile"


def test_header_sign_out_signs_out(client: FlaskClient) -> None:
    schemes_page = SchemesPage.open(client)

    assert schemes_page.header.sign_out_url == "/auth/logout"


def test_schemes_shows_authority(client: FlaskClient) -> None:
    schemes_page = SchemesPage.open(client)

    assert schemes_page.authority == "Liverpool City Region Combined Authority"


def test_schemes_shows_schemes(schemes: SchemeRepository, client: FlaskClient) -> None:
    scheme1 = Scheme(id_=1, name="Wirral Package", authority_id=1)
    scheme1.funding_programme = FundingProgramme.ATF3
    schemes.add(
        scheme1,
        Scheme(id_=2, name="School Streets", authority_id=1),
        Scheme(id_=3, name="Hospital Fields Road", authority_id=2),
    )

    schemes_page = SchemesPage.open(client)

    assert schemes_page.schemes
    assert schemes_page.schemes.to_dicts() == [
        {"reference": "ATE00001", "funding_programme": "ATF3", "name": "Wirral Package"},
        {"reference": "ATE00002", "funding_programme": "N/A", "name": "School Streets"},
    ]
    assert not schemes_page.is_no_schemes_message_visible


def test_scheme_shows_scheme(schemes: SchemeRepository, client: FlaskClient) -> None:
    schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

    schemes_page = SchemesPage.open(client)

    assert schemes_page.schemes
    assert schemes_page.schemes["ATE00001"].reference_url == "/schemes/1"


def test_schemes_shows_message_when_no_schemes(client: FlaskClient) -> None:
    schemes_page = SchemesPage.open(client)

    assert not schemes_page.schemes
    assert schemes_page.is_no_schemes_message_visible


class TestApiEnabled:
    @pytest.fixture(name="config")
    def config_fixture(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        return dict(config) | {"API_KEY": "boardman"}

    def test_clear_schemes(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        response = client.delete("/schemes", headers={"Authorization": "API-Key boardman"})

        assert response.status_code == 204
        assert not schemes.get(1)

    def test_cannot_clear_schemes_when_no_credentials(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        response = client.delete("/schemes")

        assert response.status_code == 401
        assert schemes.get(1)

    def test_cannot_clear_schemes_when_incorrect_credentials(
        self, schemes: SchemeRepository, client: FlaskClient
    ) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        response = client.delete("/schemes", headers={"Authorization": "API-Key obree"})

        assert response.status_code == 401
        assert schemes.get(1)


class TestApiDisabled:
    def test_cannot_clear_schemes(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        response = client.delete("/schemes", headers={"Authorization": "API-Key boardman"})

        assert response.status_code == 401
        assert schemes.get(1)
