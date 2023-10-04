import pytest
from flask import Flask
from playwright.sync_api import Page, expect

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


@pytest.mark.oidc_user(id="stub_user", email="user@domain.com")
class TestAuthenticated:
    @pytest.mark.usefixtures("live_server", "oidc_server")
    def test_landing_shows_home(self, app: Flask, page: Page) -> None:
        landing_page = LandingPage(app, page).open()
        landing_page.start()

        home_page = landing_page.open_when_authenticated()

        assert home_page.visible()
