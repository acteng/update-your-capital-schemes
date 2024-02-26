import pytest
from playwright.sync_api import Page

from tests.e2e.app_client import (
    AppClient,
    AuthorityRepr,
    AuthorityReviewRepr,
    SchemeRepr,
    UserRepr,
)
from tests.e2e.oidc_server.users import StubUser
from tests.e2e.oidc_server.web_client import OidcClient
from tests.e2e.pages import SchemePage


@pytest.mark.usefixtures("live_server", "oidc_server")
def test_scheme(app_client: AppClient, oidc_client: OidcClient, page: Page) -> None:
    app_client.set_clock("2023-04-24T12:00:00")
    app_client.add_authorities(AuthorityRepr(id=1, name="Liverpool City Region Combined Authority"))
    app_client.add_users(1, UserRepr(email="boardman@example.com"))
    app_client.add_schemes(
        1,
        SchemeRepr(
            id=1,
            name="Wirral Package",
            authority_reviews=[AuthorityReviewRepr(id=1, review_date="2023-01-02", source="ATF4 Bid")],
        ),
    )
    oidc_client.add_user(StubUser("boardman", "boardman@example.com"))

    scheme_page = SchemePage.open(page, id_=1)

    assert (
        scheme_page.authority == "Liverpool City Region Combined Authority"
        and scheme_page.name == "Wirral Package"
        and scheme_page.needs_review
    )
