import pytest
from flask import Flask
from playwright.sync_api import Page, expect

from tests.e2e.pages import HomePage


@pytest.mark.oidc_user(id="stub_user", email="user@domain.com")
class TestAuthenticated:
    @pytest.mark.usefixtures("live_server", "oidc_server")
    def test_home_when_authenticated(self, app: Flask, page: Page) -> None:
        home_page = HomePage(app, page).open()

        expect(home_page.header).to_contain_text("Home")


class TestUnauthenticated:
    @pytest.mark.usefixtures("live_server", "oidc_server")
    def test_home_when_unauthenticated(self, app: Flask, page: Page) -> None:
        login_page = HomePage(app, page).open_when_unauthenticated()

        assert login_page.visible()
