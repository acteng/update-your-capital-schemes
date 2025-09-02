import pytest
from playwright.sync_api import Page

from tests.e2e.api_client import (
    ApiClient,
    AuthorityModel,
    CapitalSchemeAuthorityReviewModel,
    CapitalSchemeBidStatusDetailsModel,
    CapitalSchemeMilestonesModel,
    CapitalSchemeModel,
    CapitalSchemeOverviewModel,
    FundingProgrammeModel,
    MilestoneModel,
)
from tests.e2e.app_client import AppClient, AuthorityRepr, AuthorityReviewRepr, UserRepr
from tests.e2e.builders import build_scheme
from tests.e2e.oidc_server.users import StubUser
from tests.e2e.oidc_server.web_client import OidcClient
from tests.e2e.pages import SchemesPage


@pytest.mark.usefixtures("live_server", "oidc_server")
class TestAuthenticated:
    @pytest.fixture(autouse=True)
    def oidc_user(self, oidc_client: OidcClient) -> None:
        oidc_client.add_user(StubUser("boardman", "boardman@example.com"))

    def test_schemes(self, app_client: AppClient, api_client: ApiClient, page: Page) -> None:
        app_client.set_clock("2023-04-24T12:00:00")
        api_client.add_funding_programmes(
            FundingProgrammeModel(code="ATF3", eligibleForAuthorityUpdate=True),
            FundingProgrammeModel(code="ATF4", eligibleForAuthorityUpdate=True),
        )
        api_client.add_milestones(
            MilestoneModel(name="detailed design completed", active=True, complete=False),
            MilestoneModel(name="construction started", active=True, complete=False),
        )
        app_client.add_authorities(AuthorityRepr(abbreviation="LIV", name="Liverpool City Region Combined Authority"))
        api_client.add_authorities(
            AuthorityModel(abbreviation="LIV", fullName="Liverpool City Region Combined Authority")
        )
        app_client.add_users("LIV", UserRepr(email="boardman@example.com"))
        app_client.add_schemes(
            build_scheme(
                id_=1,
                reference="ATE00001",
                name="Wirral Package",
                authority_abbreviation="LIV",
                funding_programme="ATF3",
                authority_reviews=[AuthorityReviewRepr(id=1, review_date="2020-01-02", source="ATF3 bid")],
            ),
            build_scheme(
                id_=2,
                reference="ATE00002",
                name="School Streets",
                authority_abbreviation="LIV",
                funding_programme="ATF4",
                authority_reviews=[AuthorityReviewRepr(id=2, review_date="2020-01-03", source="ATF4 bid")],
            ),
        )
        api_client.add_schemes(
            CapitalSchemeModel(
                reference="ATE00001",
                overview=CapitalSchemeOverviewModel(
                    name="Wirral Package",
                    bidSubmittingAuthority=f"{api_client.base_url}/authorities/LIV",
                    fundingProgramme=f"{api_client.base_url}/funding-programmes/ATF3",
                ),
                bidStatusDetails=CapitalSchemeBidStatusDetailsModel(bidStatus="funded"),
                milestones=CapitalSchemeMilestonesModel(currentMilestone="detailed design completed"),
                authorityReview=CapitalSchemeAuthorityReviewModel(reviewDate="2020-01-02T00:00:00Z"),
            ),
            CapitalSchemeModel(
                reference="ATE00002",
                overview=CapitalSchemeOverviewModel(
                    name="School Streets",
                    bidSubmittingAuthority=f"{api_client.base_url}/authorities/LIV",
                    fundingProgramme=f"{api_client.base_url}/funding-programmes/ATF4",
                ),
                bidStatusDetails=CapitalSchemeBidStatusDetailsModel(bidStatus="funded"),
                milestones=CapitalSchemeMilestonesModel(currentMilestone="construction started"),
                authorityReview=CapitalSchemeAuthorityReviewModel(reviewDate="2020-01-03T00:00:00Z"),
            ),
        )

        schemes_page = SchemesPage.open(page)

        assert schemes_page.heading.caption() == "Liverpool City Region Combined Authority"
        assert schemes_page.schemes.to_dicts() == [
            {
                "reference": "ATE00001",
                "funding_programme": "ATF3",
                "name": "Wirral Package",
                "needs_review": True,
                "last_reviewed": "2 Jan 2020",
            },
            {
                "reference": "ATE00002",
                "funding_programme": "ATF4",
                "name": "School Streets",
                "needs_review": True,
                "last_reviewed": "3 Jan 2020",
            },
        ]

    def test_schemes_when_unauthorized(self, page: Page) -> None:
        forbidden_page = SchemesPage.open_when_unauthorized(page)

        assert forbidden_page.is_visible()

    def test_scheme_shows_scheme(self, app_client: AppClient, api_client: ApiClient, page: Page) -> None:
        app_client.add_authorities(AuthorityRepr(abbreviation="LIV", name="Liverpool City Region Combined Authority"))
        api_client.add_authorities(
            AuthorityModel(abbreviation="LIV", fullName="Liverpool City Region Combined Authority")
        )
        app_client.add_users("LIV", UserRepr(email="boardman@example.com"))
        app_client.add_schemes(
            build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_abbreviation="LIV")
        )

        scheme_page = SchemesPage.open(page).schemes["ATE00001"].open()

        assert scheme_page.heading.text() == "Wirral Package"

    def test_schemes_shows_update_schemes_notification(
        self, app_client: AppClient, api_client: ApiClient, page: Page
    ) -> None:
        app_client.set_clock("2023-04-24T12:00:00")
        app_client.add_authorities(AuthorityRepr(abbreviation="LIV", name="Liverpool City Region Combined Authority"))
        api_client.add_authorities(
            AuthorityModel(abbreviation="LIV", fullName="Liverpool City Region Combined Authority")
        )
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

        schemes_page = SchemesPage.open(page)

        assert schemes_page.important_notification.heading() == "You have 7 days left to update your schemes"


@pytest.mark.usefixtures("live_server", "oidc_server")
class TestUnauthenticated:
    def test_schemes_when_unauthenticated(self, page: Page) -> None:
        login_page = SchemesPage.open_when_unauthenticated(page)

        assert login_page.is_visible()
