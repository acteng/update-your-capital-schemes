import pytest
from flask import Flask
from playwright.sync_api import Page, expect

from tests.e2e.oidc_server.app import OidcServerFlask
from tests.e2e.oidc_server.users import StubUser
from tests.e2e.pages import HomePage


class TestAuthenticated:
    @pytest.fixture(name="oidc_server_app", scope="class")
    def oidc_server_app_fixture(self, oidc_server_app: OidcServerFlask) -> OidcServerFlask:
        oidc_server_app.add_user(StubUser("stub_user", "user@domain.com"))
        return oidc_server_app

    @pytest.mark.usefixtures("live_server", "oidc_server")
    def test_home_when_authenticated(self, app: Flask, page: Page) -> None:
        home_page = HomePage(app, page).open()

        expect(home_page.header).to_contain_text("Home")


class TestUnauthenticated:
    @pytest.mark.usefixtures("live_server", "oidc_server")
    def test_home_when_unauthenticated(self, app: Flask, page: Page) -> None:
        login_page = HomePage(app, page).open_when_unauthenticated()

        assert login_page.visible()
