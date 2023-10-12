import pytest
from flask import Flask
from playwright.sync_api import Page

from tests.e2e.app_client import AppClient
from tests.e2e.pages import StartPage


@pytest.mark.usefixtures("live_server")
class TestUnauthenticated:
    def test_start(self, app: Flask, page: Page) -> None:
        start_page = StartPage(app, page).open()

        assert start_page.visible()

    @pytest.mark.usefixtures("oidc_server")
    def test_start_shows_login(self, app: Flask, page: Page) -> None:
        start_page = StartPage(app, page).open()

        login_page = start_page.start_when_unauthenticated()

        assert login_page.visible()


@pytest.mark.usefixtures("live_server", "oidc_server", "oidc_user")
@pytest.mark.oidc_user(id="stub_user", email="user@domain.com")
class TestAuthenticated:
    def test_start_shows_home(self, app_client: AppClient, app: Flask, page: Page) -> None:
        app_client.add_user("user@domain.com")
        start_page = StartPage(app, page).open()
        start_page.start()

        home_page = start_page.open_when_authenticated()

        assert home_page.visible()
