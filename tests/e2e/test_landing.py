import pytest
from flask import Flask
from playwright.sync_api import Page, expect

from tests.e2e.oidc_server.app import OidcServerFlask
from tests.e2e.oidc_server.users import StubUser
from tests.e2e.pages import LandingPage


class TestUnauthenticated:
    @pytest.mark.usefixtures("live_server")
    def test_index(self, app: Flask, page: Page) -> None:
        landing_page = LandingPage(app, page).open()

        expect(landing_page.header).to_contain_text("Schemes")

    @pytest.mark.usefixtures("live_server", "oidc_server")
    def test_start_shows_login(self, app: Flask, page: Page) -> None:
        landing_page = LandingPage(app, page).open()

        login_page = landing_page.start_when_unauthenticated()

        assert login_page.visible()


class TestAuthenticated:
    @pytest.fixture(name="oidc_server_app", scope="class")
    def oidc_server_app_fixture(self, oidc_server_app: OidcServerFlask) -> OidcServerFlask:
        oidc_server_app.add_user(StubUser("stub_user", "user@domain.com"))
        return oidc_server_app
