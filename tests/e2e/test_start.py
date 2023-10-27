import pytest
from flask import Flask
from playwright.sync_api import Page

from tests.e2e.app_client import AppClient, AuthorityRepr, UserRepr
from tests.e2e.oidc_server.users import StubUser
from tests.e2e.oidc_server.web_client import OidcClient
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


@pytest.mark.usefixtures("live_server", "oidc_server")
class TestAuthenticated:
    def test_start_shows_schemes(self, oidc_client: OidcClient, app_client: AppClient, app: Flask, page: Page) -> None:
        oidc_client.add_user(StubUser("boardman", "boardman@example.com"))
        app_client.add_authorities(AuthorityRepr(id=1, name="Liverpool City Region Combined Authority"))
        app_client.add_users(1, UserRepr(email="boardman@example.com"))
        start_page = StartPage(app, page).open()
        start_page.start()

        schemes_page = start_page.open_when_authenticated()

        assert schemes_page.authority() == "Liverpool City Region Combined Authority"
