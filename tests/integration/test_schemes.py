from datetime import datetime
from typing import Any, Mapping

import pytest
from flask.testing import FlaskClient

from schemes.domain.authorities import Authority, AuthorityRepository
from schemes.domain.schemes import FundingProgramme, Scheme, SchemeRepository
from schemes.domain.users import User, UserRepository
from schemes.infrastructure.clock import Clock
from tests.integration.pages import SchemesPage


class TestSchemes:
    @pytest.fixture(name="config")
    def config_fixture(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        return dict(config) | {"GOVUK_PROFILE_URL": "https://example.com/profile"}

    @pytest.fixture(name="auth", autouse=True)
    def auth_fixture(self, authorities: AuthorityRepository, users: UserRepository, client: FlaskClient) -> None:
        authorities.add(Authority(id_=1, name="Liverpool City Region Combined Authority"))
        users.add(User(email="boardman@example.com", authority_id=1))
        with client.session_transaction() as session:
            session["user"] = {"email": "boardman@example.com"}

    def test_header_home_shows_start(self, client: FlaskClient) -> None:
        schemes_page = SchemesPage.open(client)

        assert schemes_page.header.home_url == "/"

    def test_header_profile_shows_profile(self, client: FlaskClient) -> None:
        schemes_page = SchemesPage.open(client)

        assert schemes_page.header.profile_url == "https://example.com/profile"

    def test_header_sign_out_signs_out(self, client: FlaskClient) -> None:
        schemes_page = SchemesPage.open(client)

        assert schemes_page.header.sign_out_url == "/auth/logout"

    @pytest.mark.parametrize(
        "now, expected_notification_banner",
        [
            (datetime(2020, 4, 24, 12), "You have 7 days left to update your schemes"),
            (datetime(2020, 4, 30, 12), "You have 1 day left to update your schemes"),
        ],
    )
    def test_schemes_shows_update_schemes_notification(
        self, client: FlaskClient, clock: Clock, now: datetime, expected_notification_banner: str
    ) -> None:
        clock.now = now
        schemes_page = SchemesPage.open(client)

        assert (
            schemes_page.notification_banner
            and schemes_page.notification_banner.heading == expected_notification_banner
        )

    def test_schemes_does_not_show_notification_outside_reporting_window(
        self, client: FlaskClient, clock: Clock
    ) -> None:
        clock.now = datetime(2020, 3, 1)
        schemes_page = SchemesPage.open(client)

        assert not schemes_page.notification_banner

    def test_schemes_shows_authority(self, client: FlaskClient) -> None:
        schemes_page = SchemesPage.open(client)

        assert schemes_page.authority == "Liverpool City Region Combined Authority"

    def test_schemes_shows_schemes(self, schemes: SchemeRepository, client: FlaskClient) -> None:
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
            {"reference": "ATE00002", "funding_programme": "", "name": "School Streets"},
        ]
        assert not schemes_page.is_no_schemes_message_visible

    def test_scheme_shows_scheme(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        schemes_page = SchemesPage.open(client)

        assert schemes_page.schemes
        assert schemes_page.schemes["ATE00001"].reference_url == "/schemes/1"

    def test_schemes_shows_message_when_no_schemes(self, client: FlaskClient) -> None:
        schemes_page = SchemesPage.open(client)

        assert not schemes_page.schemes
        assert schemes_page.is_no_schemes_message_visible


class TestSchemesApi:
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


class TestSchemesApiWhenDisabled:
    def test_cannot_clear_schemes(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        response = client.delete("/schemes", headers={"Authorization": "API-Key boardman"})

        assert response.status_code == 401
        assert schemes.get(1)
