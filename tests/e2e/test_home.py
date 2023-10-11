import pytest
from flask import Flask
from playwright.sync_api import Page

from tests.e2e.pages import HomePage


@pytest.mark.usefixtures("live_server", "oidc_server", "oidc_user")
@pytest.mark.oidc_user(id="stub_user", email="user@domain.com")
class TestAuthenticated:
    def test_home_when_authenticated(self, app: Flask, page: Page) -> None:
        home_page = HomePage(app, page).open()

        assert home_page.visible()

    def test_header_sign_out(self, app: Flask, page: Page) -> None:
        home_page = HomePage(app, page).open()

        start_page = home_page.header.sign_out()

        assert start_page.visible()


@pytest.mark.usefixtures("live_server", "oidc_server")
class TestUnauthenticated:
    def test_home_when_unauthenticated(self, app: Flask, page: Page) -> None:
        login_page = HomePage(app, page).open_when_unauthenticated()

        assert login_page.visible()
