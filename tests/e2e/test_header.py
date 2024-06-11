import pytest
from playwright.sync_api import Page

from tests.e2e.app_client import AppClient, AuthorityRepr, UserRepr
from tests.e2e.oidc_server.users import StubUser
from tests.e2e.oidc_server.web_client import OidcClient
from tests.e2e.pages import SchemesPage


@pytest.mark.usefixtures("live_server", "oidc_server")
def test_sign_out(app_client: AppClient, oidc_client: OidcClient, page: Page) -> None:
    app_client.add_authorities(AuthorityRepr(id=1, name="Liverpool City Region Combined Authority"))
    app_client.add_users(1, UserRepr(email="boardman@example.com"))
    oidc_client.add_user(StubUser("boardman", "boardman@example.com"))
    schemes_page = SchemesPage.open(page)

    start_page = schemes_page.header.sign_out()

    assert start_page.is_visible
