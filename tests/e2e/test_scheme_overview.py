import pytest
from playwright.sync_api import Page

from tests.e2e.api_client import ApiClient, AuthorityModel
from tests.e2e.app_client import AppClient, AuthorityRepr, AuthorityReviewRepr, MilestoneRevisionRepr, UserRepr
from tests.e2e.builders import build_scheme
from tests.e2e.oidc_server.users import StubUser
from tests.e2e.oidc_server.web_client import OidcClient
from tests.e2e.pages import SchemePage


@pytest.mark.usefixtures("live_server", "oidc_server")
def test_scheme_overview(app_client: AppClient, api_client: ApiClient, oidc_client: OidcClient, page: Page) -> None:
    app_client.add_authorities(AuthorityRepr(abbreviation="LIV", name="Liverpool City Region Combined Authority"))
    api_client.add_authorities(AuthorityModel(abbreviation="LIV", fullName="Liverpool City Region Combined Authority"))
    app_client.add_users("LIV", UserRepr(email="boardman@example.com"))
    app_client.add_schemes(
        build_scheme(
            id_=1,
            reference="ATE00001",
            name="Wirral Package",
            authority_abbreviation="LIV",
            type_="construction",
            funding_programme="ATF4",
            milestone_revisions=[
                MilestoneRevisionRepr(
                    id=1,
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    milestone="detailed design completed",
                    observation_type="actual",
                    status_date="2020-01-01",
                    source="ATF4 bid",
                )
            ],
            authority_reviews=[AuthorityReviewRepr(id=1, review_date="2020-01-02", source="ATF4 bid")],
        ),
    )
    oidc_client.add_user(StubUser("boardman", "boardman@example.com"))

    scheme_page = SchemePage.open(page, reference="ATE00001")

    assert (
        scheme_page.overview.reference == "ATE00001"
        and scheme_page.overview.scheme_type == "Construction"
        and scheme_page.overview.funding_programme == "ATF4"
        and scheme_page.overview.current_milestone == "Detailed design completed"
    )
