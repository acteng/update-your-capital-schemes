import pytest
from playwright.sync_api import Page

from tests.e2e.api_client import (
    ApiClient,
    AuthorityModel,
    CapitalSchemeMilestoneModel,
    CapitalSchemeMilestonesModel,
    FundingProgrammeModel,
    ImprovementModel,
    ImprovementOverviewModel,
    build_capital_scheme_model,
)
from tests.e2e.app_client import AppClient, UserRepr
from tests.e2e.oidc_server.users import StubUser
from tests.e2e.oidc_server.web_client import OidcClient
from tests.e2e.pages import SchemePage


@pytest.mark.usefixtures("live_server", "oidc_server")
def test_scheme_overview(app_client: AppClient, api_client: ApiClient, oidc_client: OidcClient, page: Page) -> None:
    api_client.add_funding_programmes(FundingProgrammeModel(code="ATF4", eligible_for_authority_update=True))
    api_client.add_authorities(AuthorityModel(abbreviation="LIV", full_name="Liverpool City Region Combined Authority"))
    api_client.add_improvements(
        ImprovementModel(
            reference="IMP00001",
            overview=ImprovementOverviewModel(
                name="Wirral Package",
                description='Improvement for the "Wirral Package" capital scheme created as part of funding devolution.',
                funding_managed_by=f"{api_client.base_url}/authorities/LIV",
                source="authority update",
            ),
        )
    )
    api_client.add_schemes(
        build_capital_scheme_model(
            reference="ATE00001",
            name="Wirral Package",
            funding_programme=f"{api_client.base_url}/funding-programmes/ATF4",
            improvement=f"{api_client.base_url}/improvements/IMP00001",
            type_="construction",
            milestones=CapitalSchemeMilestonesModel(
                current_milestone="detailed design completed",
                items=[
                    CapitalSchemeMilestoneModel(
                        milestone="detailed design completed",
                        observation_type="actual",
                        status_date="2020-01-01",
                        source="ATF4 bid",
                    )
                ],
            ),
        )
    )
    app_client.add_users(UserRepr(email="boardman@example.com", authority_abbreviation="LIV"))
    oidc_client.add_user(StubUser("boardman", "boardman@example.com"))

    scheme_page = SchemePage.open(page, reference="ATE00001")

    assert (
        scheme_page.overview.reference == "ATE00001"
        and scheme_page.overview.scheme_type == "Construction"
        and scheme_page.overview.funding_programme == "ATF4"
        and scheme_page.overview.current_milestone == "Detailed design completed"
    )
