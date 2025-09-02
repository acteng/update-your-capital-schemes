import pytest
from playwright.async_api import Page

from tests.e2e.api_client import ApiClient, AuthorityModel
from tests.e2e.app_client import AppClient, AuthorityRepr, UserRepr
from tests.e2e.oidc_server.users import StubUser
from tests.e2e.oidc_server.web_client import OidcClient
from tests.e2e.pages import StartPage

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest.mark.usefixtures("live_server")
class TestUnauthenticated:
    async def test_start(self, page: Page) -> None:
        start_page = await StartPage.open(page)

        assert await start_page.is_visible()

    @pytest.mark.usefixtures("oidc_server")
    async def test_start_shows_login(self, page: Page) -> None:
        start_page = await StartPage.open(page)

        login_page = await start_page.start_when_unauthenticated()

        assert await login_page.is_visible()


@pytest.mark.usefixtures("live_server", "oidc_server")
class TestAuthenticated:
    async def test_start_shows_schemes(
        self, oidc_client: OidcClient, app_client: AppClient, api_client: ApiClient, page: Page
    ) -> None:
        oidc_client.add_user(StubUser("boardman", "boardman@example.com"))
        app_client.add_authorities(AuthorityRepr(abbreviation="LIV", name="Liverpool City Region Combined Authority"))
        api_client.add_authorities(
            AuthorityModel(abbreviation="LIV", fullName="Liverpool City Region Combined Authority")
        )
        app_client.add_users("LIV", UserRepr(email="boardman@example.com"))
        start_page = await StartPage.open(page)
        await start_page.start()

        schemes_page = await StartPage.open_when_authenticated(page)

        assert await schemes_page.heading.caption() == "Liverpool City Region Combined Authority"
