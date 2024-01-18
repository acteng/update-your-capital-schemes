import pytest
from playwright.sync_api import Page

from tests.e2e.app_client import (
    AppClient,
    AuthorityRepr,
    FinancialRevisionRepr,
    SchemeRepr,
    UserRepr,
)
from tests.e2e.oidc_server.users import StubUser
from tests.e2e.oidc_server.web_client import OidcClient
from tests.e2e.pages import SchemePage


@pytest.mark.usefixtures("live_server", "oidc_server")
def test_scheme_funding(app_client: AppClient, oidc_client: OidcClient, page: Page) -> None:
    app_client.add_authorities(AuthorityRepr(id=1, name="Liverpool City Region Combined Authority"))
    app_client.add_users(1, UserRepr(email="boardman@example.com"))
    app_client.add_schemes(
        1,
        SchemeRepr(
            id=1,
            name="Wirral Package",
            financial_revisions=[
                FinancialRevisionRepr(
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    type="funding allocation",
                    amount=100_000,
                    source="ATF4 Bid",
                ),
                FinancialRevisionRepr(
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    type="funding allocation",
                    amount=10_000,
                    source="Change Control",
                ),
                FinancialRevisionRepr(
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    type="spent to date",
                    amount=50_000,
                    source="ATF4 Bid",
                ),
            ],
        ),
    )
    oidc_client.add_user(StubUser("boardman", "boardman@example.com"))

    scheme_page = SchemePage.open(page, id_=1)

    assert (
        scheme_page.funding.funding_allocation == "£100,000"
        and scheme_page.funding.change_control_adjustment == "£10,000"
        and scheme_page.funding.spend_to_date == "£50,000"
        and scheme_page.funding.allocation_still_to_spend == "£60,000"
    )
