import pytest
from playwright.async_api import Page

from tests.e2e.api_client import ApiClient, AuthorityModel
from tests.e2e.app_client import AppClient, AuthorityRepr, AuthorityReviewRepr, UserRepr
from tests.e2e.builders import build_scheme
from tests.e2e.oidc_server.users import StubUser
from tests.e2e.oidc_server.web_client import OidcClient
from tests.e2e.pages import SchemePage

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest.mark.usefixtures("live_server", "oidc_server")
async def test_scheme(app_client: AppClient, api_client: ApiClient, oidc_client: OidcClient, page: Page) -> None:
    app_client.set_clock("2023-04-24T12:00:00")
    app_client.add_authorities(AuthorityRepr(abbreviation="LIV", name="Liverpool City Region Combined Authority"))
    api_client.add_authorities(AuthorityModel(abbreviation="LIV", fullName="Liverpool City Region Combined Authority"))
    app_client.add_users("LIV", UserRepr(email="boardman@example.com"))
    app_client.add_schemes(
        build_scheme(
            id_=1,
            reference="ATE00001",
            name="Wirral Package",
            authority_abbreviation="LIV",
            authority_reviews=[AuthorityReviewRepr(id=1, review_date="2023-01-02", source="ATF4 bid")],
        ),
    )
    oidc_client.add_user(StubUser("boardman", "boardman@example.com"))

    scheme_page = await SchemePage.open(page, reference="ATE00001")

    assert (
        await scheme_page.heading.caption() == "Liverpool City Region Combined Authority"
        and await scheme_page.heading.text() == "Wirral Package"
        and await scheme_page.needs_review()
    )
