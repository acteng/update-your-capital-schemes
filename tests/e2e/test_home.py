import pytest
from flask import Flask
from playwright.sync_api import Page

from tests.e2e.app_client import AppClient
from tests.e2e.oidc_server.users import StubUser
from tests.e2e.oidc_server.web_client import OidcClient
from tests.e2e.pages import HomePage


@pytest.mark.usefixtures("live_server", "oidc_server")
class TestAuthenticated:
    @pytest.fixture(autouse=True)
    def oidc_user(self, oidc_client: OidcClient) -> None:
        oidc_client.add_user(StubUser("boardman", "boardman@example.com"))

    def test_home_when_authorized(self, app_client: AppClient, app: Flask, page: Page) -> None:
        app_client.add_user("boardman@example.com")

        home_page = HomePage(app, page).open()

        assert home_page.visible()

    def test_home_when_unauthorized(self, app: Flask, page: Page) -> None:
        unauthorized_page = HomePage(app, page).open_when_unauthorized()

        assert unauthorized_page.visible()

    def test_header_sign_out(self, app_client: AppClient, app: Flask, page: Page) -> None:
        app_client.add_user("boardman@example.com")
        home_page = HomePage(app, page).open()

        start_page = home_page.header.sign_out()

        assert start_page.visible()


@pytest.mark.usefixtures("live_server", "oidc_server")
class TestUnauthenticated:
    def test_home_when_unauthenticated(self, app: Flask, page: Page) -> None:
        login_page = HomePage(app, page).open_when_unauthenticated()

        assert login_page.visible()
