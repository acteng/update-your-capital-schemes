import pytest
from playwright.sync_api import Page

from tests.e2e.api_client import (
    ApiClient,
    AuthorityModel,
    CapitalSchemeBidStatusDetailsModel,
    CapitalSchemeFinancialModel,
    CapitalSchemeMilestonesModel,
    CapitalSchemeModel,
    CapitalSchemeOutputModel,
    CapitalSchemeOverviewModel,
    CollectionModel,
    FundingProgrammeModel,
)
from tests.e2e.app_client import AppClient, AuthorityRepr, OutputRevisionRepr, UserRepr
from tests.e2e.builders import build_scheme
from tests.e2e.oidc_server.users import StubUser
from tests.e2e.oidc_server.web_client import OidcClient
from tests.e2e.pages import SchemePage


@pytest.mark.usefixtures("live_server", "oidc_server")
def test_scheme_outputs(app_client: AppClient, api_client: ApiClient, oidc_client: OidcClient, page: Page) -> None:
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
            output_revisions=[
                OutputRevisionRepr(
                    id=1,
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    type="new segregated cycling facility",
                    measure="miles",
                    value="3.000000",
                    observation_type="planned",
                ),
                OutputRevisionRepr(
                    id=2,
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    type="improvements to make an existing walking/cycle route safer",
                    measure="number of junctions",
                    value="2.600000",
                    observation_type="planned",
                ),
            ],
        ),
    )
    api_client.add_schemes(
        CapitalSchemeModel(
            reference="ATE00001",
            overview=CapitalSchemeOverviewModel(
                name="Wirral Package",
                bidSubmittingAuthority=f"{api_client.base_url}/authorities/LIV",
                fundingProgramme=f"{api_client.base_url}/funding-programmes/ATF2",
                type="construction",
            ),
            bidStatusDetails=CapitalSchemeBidStatusDetailsModel(bidStatus="funded"),
            financials=CollectionModel[CapitalSchemeFinancialModel](items=[]),
            milestones=CapitalSchemeMilestonesModel(currentMilestone=None, items=[]),
            outputs=CollectionModel[CapitalSchemeOutputModel](
                items=[
                    CapitalSchemeOutputModel(
                        type="new segregated cycling facility",
                        measure="miles",
                        observationType="planned",
                        value="3.000000",
                    ),
                    CapitalSchemeOutputModel(
                        type="improvements to make an existing walking/cycle route safer",
                        measure="number of junctions",
                        observationType="planned",
                        value="2.600000",
                    ),
                ]
            ),
            authorityReview=None,
        )
    )
    oidc_client.add_user(StubUser("boardman", "boardman@example.com"))

    scheme_page = SchemePage.open(page, reference="ATE00001")

    assert scheme_page.outputs.outputs.to_dicts() == [
        {
            "infrastructure": "New segregated cycling facility",
            "measurement": "Miles",
            "planned": "3",
        },
        {
            "infrastructure": "Improvements to make an existing walking/cycle route safer",
            "measurement": "Number of junctions",
            "planned": "2.6",
        },
    ]
