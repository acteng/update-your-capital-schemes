import pytest
from playwright.sync_api import Page

from tests.e2e.api_client import ApiClient
from tests.e2e.api_client import AuthorityRepr as ApiAuthorityRepr
from tests.e2e.app_client import AppClient, AuthorityRepr, UserRepr
from tests.e2e.oidc_server.users import StubUser
from tests.e2e.oidc_server.web_client import OidcClient
from tests.e2e.pages import StartPage


@pytest.mark.usefixtures("live_server")
class TestUnauthenticated:
    def test_start(self, page: Page) -> None:
        start_page = StartPage.open(page)

        assert start_page.is_visible

    @pytest.mark.usefixtures("oidc_server")
    def test_start_shows_login(self, page: Page) -> None:
        start_page = StartPage.open(page)

        login_page = start_page.start_when_unauthenticated()

        assert login_page.is_visible


@pytest.mark.usefixtures("live_server", "oidc_server")
class TestAuthenticated:
    def test_start_shows_schemes(
        self, oidc_client: OidcClient, app_client: AppClient, api_client: ApiClient, page: Page
    ) -> None:
        oidc_client.add_user(StubUser("boardman", "boardman@example.com"))
        app_client.add_authorities(AuthorityRepr(abbreviation="LIV", name="Liverpool City Region Combined Authority"))
        api_client.add_authorities(
            ApiAuthorityRepr(abbreviation="LIV", fullName="Liverpool City Region Combined Authority")
        )
        app_client.add_users("LIV", UserRepr(email="boardman@example.com"))
        start_page = StartPage.open(page)
        start_page.start()

        schemes_page = StartPage.open_when_authenticated(page)

        assert schemes_page.heading.caption == "Liverpool City Region Combined Authority"
