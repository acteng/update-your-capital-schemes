import pytest
from playwright.sync_api import Page

from tests.e2e.api_client import ApiClient, AuthorityModel
from tests.e2e.app_client import AppClient, UserRepr
from tests.e2e.oidc_server.users import StubUser
from tests.e2e.oidc_server.web_client import OidcClient
from tests.e2e.pages import SchemesPage


@pytest.mark.usefixtures("live_server", "oidc_server")
def test_sign_out(app_client: AppClient, api_client: ApiClient, oidc_client: OidcClient, page: Page) -> None:
    api_client.add_authorities(AuthorityModel(abbreviation="LIV", full_name="Liverpool City Region Combined Authority"))
    app_client.add_users(UserRepr(email="boardman@example.com", authority_abbreviation="LIV"))
    oidc_client.add_user(StubUser("boardman", "boardman@example.com"))
    schemes_page = SchemesPage.open(page)

    start_page = schemes_page.header.sign_out()

    assert start_page.is_visible
