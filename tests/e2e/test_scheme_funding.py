import pytest
from flask import Flask
from playwright.sync_api import Page

from tests.e2e.api_client import ApiClient, AuthorityModel, CapitalSchemeFinancialModel, FundingProgrammeModel
from tests.e2e.app_client import AppClient, AuthorityRepr, FinancialRevisionRepr, UserRepr
from tests.e2e.builders import build_capital_scheme_model, build_scheme
from tests.e2e.oidc_server.users import StubUser
from tests.e2e.oidc_server.web_client import OidcClient
from tests.e2e.pages import SchemePage


@pytest.mark.usefixtures("live_server", "oidc_server")
def test_scheme_funding(app_client: AppClient, api_client: ApiClient, oidc_client: OidcClient, page: Page) -> None:
    api_client.add_funding_programmes(FundingProgrammeModel(code="ATF2", eligibleForAuthorityUpdate=True))
    app_client.add_authorities(AuthorityRepr(abbreviation="LIV", name="Liverpool City Region Combined Authority"))
    api_client.add_authorities(AuthorityModel(abbreviation="LIV", fullName="Liverpool City Region Combined Authority"))
    app_client.add_users("LIV", UserRepr(email="boardman@example.com"))
    app_client.add_schemes(
        build_scheme(
            id_=1,
            reference="ATE00001",
            name="Wirral Package",
            authority_abbreviation="LIV",
            financial_revisions=[
                FinancialRevisionRepr(
                    id=1,
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    type="funding allocation",
                    amount=100_000,
                    source="ATF4 bid",
                ),
                FinancialRevisionRepr(
                    id=2,
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    type="spend to date",
                    amount=50_000,
                    source="ATF4 bid",
                ),
            ],
        ),
    )
    api_client.add_schemes(
        build_capital_scheme_model(
            reference="ATE00001",
            name="Wirral Package",
            bid_submitting_authority=f"{api_client.base_url}/authorities/LIV",
            funding_programme=f"{api_client.base_url}/funding-programmes/ATF2",
            financials=[
                CapitalSchemeFinancialModel(type="funding allocation", amount=100_000),
                CapitalSchemeFinancialModel(type="spend to date", amount=50_000),
            ],
        )
    )
    oidc_client.add_user(StubUser("boardman", "boardman@example.com"))

    scheme_page = SchemePage.open(page, reference="ATE00001")

    assert (
        scheme_page.funding.funding_allocation == "£100,000"
        and scheme_page.funding.spend_to_date == "£50,000"
        and scheme_page.funding.allocation_still_to_spend == "£50,000"
    )


@pytest.mark.usefixtures("live_server", "oidc_server")
def test_change_spend_to_date(
    app: Flask, app_client: AppClient, api_client: ApiClient, oidc_client: OidcClient, page: Page
) -> None:
    app_client.set_clock("2020-01-31T13:00:00")
    api_client.add_funding_programmes(FundingProgrammeModel(code="ATF2", eligibleForAuthorityUpdate=True))
    app_client.add_authorities(AuthorityRepr(abbreviation="LIV", name="Liverpool City Region Combined Authority"))
    api_client.add_authorities(AuthorityModel(abbreviation="LIV", fullName="Liverpool City Region Combined Authority"))
    app_client.add_users("LIV", UserRepr(email="boardman@example.com"))
    app_client.add_schemes(
        build_scheme(
            id_=1,
            reference="ATE00001",
            name="Wirral Package",
            authority_abbreviation="LIV",
            financial_revisions=[
                FinancialRevisionRepr(
                    id=1,
                    effective_date_from="2020-01-01T12:00:00",
                    effective_date_to=None,
                    type="funding allocation",
                    amount=100_000,
                    source="ATF4 bid",
                ),
                FinancialRevisionRepr(
                    id=2,
                    effective_date_from="2020-01-01T12:00:00",
                    effective_date_to=None,
                    type="spend to date",
                    amount=50_000,
                    source="ATF4 bid",
                ),
            ],
        ),
    )
    api_client.add_schemes(
        build_capital_scheme_model(
            reference="ATE00001",
            name="Wirral Package",
            bid_submitting_authority=f"{api_client.base_url}/authorities/LIV",
            funding_programme=f"{api_client.base_url}/funding-programmes/ATF2",
            financials=[
                CapitalSchemeFinancialModel(type="funding allocation", amount=100_000),
                CapitalSchemeFinancialModel(type="spend to date", amount=50_000),
            ],
        )
    )
    oidc_client.add_user(StubUser("boardman", "boardman@example.com"))

    scheme_page = (
        SchemePage.open(page, reference="ATE00001").funding.change_spend_to_date().form.enter_amount("60000").confirm()
    )

    assert scheme_page.heading.text == "Wirral Package"
    # TODO: reinstate when https://github.com/acteng/update-your-capital-schemes/issues/189 resolved
    if "ATE_URL" not in app.config:
        assert scheme_page.funding.spend_to_date == "£60,000"
    assert app_client.get_scheme(reference="ATE00001").financial_revisions == [
        FinancialRevisionRepr(
            id=1,
            effective_date_from="2020-01-01T12:00:00",
            effective_date_to=None,
            type="funding allocation",
            amount=100_000,
            source="ATF4 bid",
        ),
        FinancialRevisionRepr(
            id=2,
            effective_date_from="2020-01-01T12:00:00",
            effective_date_to="2020-01-31T13:00:00",
            type="spend to date",
            amount=50_000,
            source="ATF4 bid",
        ),
        FinancialRevisionRepr(
            id=3,
            effective_date_from="2020-01-31T13:00:00",
            effective_date_to=None,
            type="spend to date",
            amount=60_000,
            source="authority update",
        ),
    ]


@pytest.mark.usefixtures("live_server", "oidc_server")
def test_cannot_change_spend_to_date_when_error(
    app_client: AppClient, api_client: ApiClient, oidc_client: OidcClient, page: Page
) -> None:
    api_client.add_funding_programmes(FundingProgrammeModel(code="ATF2", eligibleForAuthorityUpdate=True))
    app_client.add_authorities(AuthorityRepr(abbreviation="LIV", name="Liverpool City Region Combined Authority"))
    api_client.add_authorities(AuthorityModel(abbreviation="LIV", fullName="Liverpool City Region Combined Authority"))
    app_client.add_users("LIV", UserRepr(email="boardman@example.com"))
    app_client.add_schemes(
        build_scheme(
            id_=1,
            reference="ATE00001",
            name="Wirral Package",
            authority_abbreviation="LIV",
            financial_revisions=[
                FinancialRevisionRepr(
                    id=1,
                    effective_date_from="2020-01-01T12:00:00",
                    effective_date_to=None,
                    type="funding allocation",
                    amount=100_000,
                    source="ATF4 bid",
                ),
                FinancialRevisionRepr(
                    id=2,
                    effective_date_from="2020-01-01T12:00:00",
                    effective_date_to=None,
                    type="spend to date",
                    amount=50_000,
                    source="ATF4 bid",
                ),
            ],
        ),
    )
    api_client.add_schemes(
        build_capital_scheme_model(
            reference="ATE00001",
            name="Wirral Package",
            bid_submitting_authority=f"{api_client.base_url}/authorities/LIV",
            funding_programme=f"{api_client.base_url}/funding-programmes/ATF2",
            financials=[
                CapitalSchemeFinancialModel(type="funding allocation", amount=100_000),
                CapitalSchemeFinancialModel(type="spend to date", amount=50_000),
            ],
        )
    )
    oidc_client.add_user(StubUser("boardman", "boardman@example.com"))

    change_spend_to_date_page = (
        SchemePage.open(page, reference="ATE00001")
        .funding.change_spend_to_date()
        .form.enter_amount("")
        .confirm_when_error()
    )

    assert (
        change_spend_to_date_page.title
        == "Error: How much has been spent to date? - Update your capital schemes - Active Travel England - GOV.UK"
    )
    assert list(change_spend_to_date_page.errors) == ["Enter spend to date"]
    assert (
        change_spend_to_date_page.form.amount.is_errored
        and change_spend_to_date_page.form.amount.error == "Error: Enter spend to date"
        and change_spend_to_date_page.form.amount.value == ""
    )
    assert app_client.get_scheme(reference="ATE00001").financial_revisions == [
        FinancialRevisionRepr(
            id=1,
            effective_date_from="2020-01-01T12:00:00",
            effective_date_to=None,
            type="funding allocation",
            amount=100_000,
            source="ATF4 bid",
        ),
        FinancialRevisionRepr(
            id=2,
            effective_date_from="2020-01-01T12:00:00",
            effective_date_to=None,
            type="spend to date",
            amount=50_000,
            source="ATF4 bid",
        ),
    ]
