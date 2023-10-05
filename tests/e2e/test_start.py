import pytest
from flask import Flask
from playwright.sync_api import Page

from tests.e2e.pages import StartPage


class TestUnauthenticated:
    @pytest.mark.usefixtures("live_server")
    def test_start(self, app: Flask, page: Page) -> None:
        start_page = StartPage(app, page).open()

        assert start_page.visible()

    @pytest.mark.usefixtures("live_server", "oidc_server")
    def test_start_shows_login(self, app: Flask, page: Page) -> None:
        start_page = StartPage(app, page).open()

        login_page = start_page.start_when_unauthenticated()

        assert login_page.visible()


@pytest.mark.oidc_user(id="stub_user", email="user@domain.com")
class TestAuthenticated:
    @pytest.mark.usefixtures("live_server", "oidc_server")
    def test_start_shows_home(self, app: Flask, page: Page) -> None:
        start_page = StartPage(app, page).open()
        start_page.start()

        home_page = start_page.open_when_authenticated()

        assert home_page.visible()
