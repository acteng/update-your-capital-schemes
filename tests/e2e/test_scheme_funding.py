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
                    id=1,
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    type="funding allocation",
                    amount=100_000,
                    source="ATF4 Bid",
                ),
                FinancialRevisionRepr(
                    id=2,
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    type="funding allocation",
                    amount=10_000,
                    source="Change Control",
                ),
                FinancialRevisionRepr(
                    id=3,
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


@pytest.mark.usefixtures("live_server", "oidc_server")
def test_change_spend_to_date(app_client: AppClient, oidc_client: OidcClient, page: Page) -> None:
    app_client.set_clock("2020-01-31T13:00:00")
    app_client.add_authorities(AuthorityRepr(id=1, name="Liverpool City Region Combined Authority"))
    app_client.add_users(1, UserRepr(email="boardman@example.com"))
    app_client.add_schemes(
        1,
        SchemeRepr(
            id=1,
            name="Wirral Package",
            financial_revisions=[
                FinancialRevisionRepr(
                    id=1,
                    effective_date_from="2020-01-01T12:00:00",
                    effective_date_to=None,
                    type="funding allocation",
                    amount=100_000,
                    source="ATF4 Bid",
                ),
                FinancialRevisionRepr(
                    id=2,
                    effective_date_from="2020-01-01T12:00:00",
                    effective_date_to=None,
                    type="spent to date",
                    amount=50_000,
                    source="ATF4 Bid",
                ),
            ],
        ),
    )
    oidc_client.add_user(StubUser("boardman", "boardman@example.com"))

    scheme_page = SchemePage.open(page, id_=1).funding.change_spend_to_date().enter_amount("60000").confirm()

    assert scheme_page.name == "Wirral Package" and scheme_page.funding.spend_to_date == "£60,000"
    assert app_client.get_scheme(id_=1).financial_revisions == [
        FinancialRevisionRepr(
            id=1,
            effective_date_from="2020-01-01T12:00:00",
            effective_date_to=None,
            type="funding allocation",
            amount=100_000,
            source="ATF4 Bid",
        ),
        FinancialRevisionRepr(
            id=2,
            effective_date_from="2020-01-01T12:00:00",
            effective_date_to="2020-01-31T13:00:00",
            type="spent to date",
            amount=50_000,
            source="ATF4 Bid",
        ),
        FinancialRevisionRepr(
            id=3,
            effective_date_from="2020-01-31T13:00:00",
            effective_date_to=None,
            type="spent to date",
            amount=60_000,
            source="Authority Update",
        ),
    ]


@pytest.mark.usefixtures("live_server", "oidc_server")
def test_cannot_change_spend_to_date_when_error(app_client: AppClient, oidc_client: OidcClient, page: Page) -> None:
    app_client.add_authorities(AuthorityRepr(id=1, name="Liverpool City Region Combined Authority"))
    app_client.add_users(1, UserRepr(email="boardman@example.com"))
    app_client.add_schemes(
        1,
        SchemeRepr(
            id=1,
            name="Wirral Package",
            financial_revisions=[
                FinancialRevisionRepr(
                    id=1,
                    effective_date_from="2020-01-01T12:00:00",
                    effective_date_to=None,
                    type="funding allocation",
                    amount=100_000,
                    source="ATF4 Bid",
                ),
                FinancialRevisionRepr(
                    id=2,
                    effective_date_from="2020-01-01T12:00:00",
                    effective_date_to=None,
                    type="spent to date",
                    amount=50_000,
                    source="ATF4 Bid",
                ),
            ],
        ),
    )
    oidc_client.add_user(StubUser("boardman", "boardman@example.com"))

    change_spend_to_date_page = (
        SchemePage.open(page, id_=1).funding.change_spend_to_date().enter_amount("").confirm_when_error()
    )

    assert change_spend_to_date_page.title == "Error: Schemes - Active Travel England - GOV.UK"
    assert list(change_spend_to_date_page.errors) == ["Enter an amount"]
    assert (
        change_spend_to_date_page.amount.is_errored
        and change_spend_to_date_page.amount.error == "Error: Enter an amount"
        and change_spend_to_date_page.amount.value == ""
    )
    assert app_client.get_scheme(id_=1).financial_revisions == [
        FinancialRevisionRepr(
            id=1,
            effective_date_from="2020-01-01T12:00:00",
            effective_date_to=None,
            type="funding allocation",
            amount=100_000,
            source="ATF4 Bid",
        ),
        FinancialRevisionRepr(
            id=2,
            effective_date_from="2020-01-01T12:00:00",
            effective_date_to=None,
            type="spent to date",
            amount=50_000,
            source="ATF4 Bid",
        ),
    ]
