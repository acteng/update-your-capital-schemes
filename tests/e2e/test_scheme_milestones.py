import pytest
from playwright.sync_api import Page

from tests.e2e.app_client import (
    AppClient,
    AuthorityRepr,
    MilestoneRevisionRepr,
    SchemeRepr,
    UserRepr,
)
from tests.e2e.oidc_server.users import StubUser
from tests.e2e.oidc_server.web_client import OidcClient
from tests.e2e.pages import SchemePage


@pytest.mark.usefixtures("live_server", "oidc_server")
def test_scheme_milestones(app_client: AppClient, oidc_client: OidcClient, page: Page) -> None:
    app_client.add_authorities(AuthorityRepr(id=1, name="Liverpool City Region Combined Authority"))
    app_client.add_users(1, UserRepr(email="boardman@example.com"))
    app_client.add_schemes(
        1,
        SchemeRepr(
            id=1,
            name="Wirral Package",
            milestone_revisions=[
                MilestoneRevisionRepr(
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    milestone="feasibility design completed",
                    observation_type="Actual",
                    status_date="2020-11-30",
                ),
                MilestoneRevisionRepr(
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    milestone="preliminary design completed",
                    observation_type="Actual",
                    status_date="2022-06-30",
                ),
                MilestoneRevisionRepr(
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    milestone="detailed design completed",
                    observation_type="Actual",
                    status_date="2022-06-30",
                ),
                MilestoneRevisionRepr(
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    milestone="construction started",
                    observation_type="Planned",
                    status_date="2023-06-05",
                ),
                MilestoneRevisionRepr(
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    milestone="construction completed",
                    observation_type="Planned",
                    status_date="2023-08-31",
                ),
            ],
        ),
    )
    oidc_client.add_user(StubUser("boardman", "boardman@example.com"))

    scheme_page = SchemePage.open(page, id_=1)

    assert scheme_page.milestones.milestones.to_dicts() == [
        {"milestone": "Feasibility design completed", "planned": "N/A", "actual": "30 Nov 2020"},
        {"milestone": "Preliminary design completed", "planned": "N/A", "actual": "30 Jun 2022"},
        {"milestone": "Detailed design completed", "planned": "N/A", "actual": "30 Jun 2022"},
        {"milestone": "Construction started", "planned": "5 Jun 2023", "actual": "N/A"},
        {"milestone": "Construction completed", "planned": "31 Aug 2023", "actual": "N/A"},
    ]
