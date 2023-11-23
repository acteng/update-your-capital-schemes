import pytest
from flask import Flask
from playwright.sync_api import Page

from tests.e2e.app_client import AppClient, AuthorityRepr, SchemeRepr, UserRepr
from tests.e2e.oidc_server.users import StubUser
from tests.e2e.oidc_server.web_client import OidcClient
from tests.e2e.pages import SchemesPage


@pytest.mark.usefixtures("live_server", "oidc_server")
class TestAuthenticated:
    @pytest.fixture(autouse=True)
    def oidc_user(self, oidc_client: OidcClient) -> None:
        oidc_client.add_user(StubUser("boardman", "boardman@example.com"))

    def test_schemes(self, app_client: AppClient, app: Flask, page: Page) -> None:
        app_client.add_authorities(AuthorityRepr(id=1, name="Liverpool City Region Combined Authority"))
        app_client.add_users(1, UserRepr(email="boardman@example.com"))
        app_client.add_schemes(
            1,
            SchemeRepr(id=1, name="Wirral Package", funding_programme="ATF3"),
            SchemeRepr(id=2, name="School Streets", funding_programme="ATF4"),
        )

        schemes_page = SchemesPage(app, page).open()

        assert schemes_page.authority == "Liverpool City Region Combined Authority"
        assert schemes_page.schemes.to_dicts() == [
            {"reference": "ATE00001", "funding_programme": "ATF3", "name": "Wirral Package"},
            {"reference": "ATE00002", "funding_programme": "ATF4", "name": "School Streets"},
        ]

    def test_schemes_when_unauthorized(self, app: Flask, page: Page) -> None:
        unauthorized_page = SchemesPage(app, page).open_when_unauthorized()

        assert unauthorized_page.is_visible

    def test_scheme_shows_scheme(self, app_client: AppClient, app: Flask, page: Page) -> None:
        app_client.add_authorities(AuthorityRepr(id=1, name="Liverpool City Region Combined Authority"))
        app_client.add_users(1, UserRepr(email="boardman@example.com"))
        app_client.add_schemes(1, SchemeRepr(id=1, name="Wirral Package"))

        scheme_page = SchemesPage(app, page).open().schemes["ATE00001"].open()

        assert scheme_page.name == "Wirral Package"

    def test_header_sign_out(self, app_client: AppClient, app: Flask, page: Page) -> None:
        app_client.add_authorities(AuthorityRepr(id=1, name="Liverpool City Region Combined Authority"))
        app_client.add_users(1, UserRepr(email="boardman@example.com"))
        schemes_page = SchemesPage(app, page).open()

        start_page = schemes_page.header.sign_out()

        assert start_page.is_visible


@pytest.mark.usefixtures("live_server", "oidc_server")
class TestUnauthenticated:
    def test_schemes_when_unauthenticated(self, app: Flask, page: Page) -> None:
        login_page = SchemesPage(app, page).open_when_unauthenticated()

        assert login_page.is_visible
