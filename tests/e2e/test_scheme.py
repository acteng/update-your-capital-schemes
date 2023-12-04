import pytest
from playwright.sync_api import Page

from tests.e2e.app_client import (
    AppClient,
    AuthorityRepr,
    FinancialRevisionRepr,
    MilestoneRevisionRepr,
    OutputRevisionRepr,
    SchemeRepr,
    UserRepr,
)
from tests.e2e.oidc_server.users import StubUser
from tests.e2e.oidc_server.web_client import OidcClient
from tests.e2e.pages import SchemePage


@pytest.mark.usefixtures("live_server", "oidc_server")
def test_scheme_overview(app_client: AppClient, oidc_client: OidcClient, page: Page) -> None:
    app_client.add_authorities(AuthorityRepr(id=1, name="Liverpool City Region Combined Authority"))
    app_client.add_users(1, UserRepr(email="boardman@example.com"))
    app_client.add_schemes(
        1,
        SchemeRepr(
            id=1,
            name="Wirral Package",
            type="construction",
            funding_programme="ATF4",
            milestone_revisions=[
                MilestoneRevisionRepr(
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    milestone="detailed design completed",
                    observation_type="Actual",
                    status_date="2020-01-01",
                )
            ],
        ),
    )
    oidc_client.add_user(StubUser("boardman", "boardman@example.com"))

    scheme_page = SchemePage(page).open(1)

    assert (
        scheme_page.name == "Wirral Package"
        and scheme_page.overview.reference == "ATE00001"
        and scheme_page.overview.scheme_type == "Construction"
        and scheme_page.overview.funding_programme == "ATF4"
        and scheme_page.overview.current_milestone == "Detailed design completed"
    )


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
                    amount="100000",
                    source="ATF4 Bid",
                ),
                FinancialRevisionRepr(
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    type="spent to date",
                    amount="50000",
                    source="ATF4 Bid",
                ),
                FinancialRevisionRepr(
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    type="funding allocation",
                    amount="10000",
                    source="change control",
                ),
            ],
        ),
    )
    oidc_client.add_user(StubUser("boardman", "boardman@example.com"))

    funding_component = SchemePage(page).open(1).open_funding()

    assert (
        funding_component.funding_allocation == "£100,000"
        and funding_component.spend_to_date == "£50,000"
        and funding_component.change_control_adjustment == "£10,000"
        and funding_component.allocation_still_to_spend == "£60,000"
    )


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

    milestones_component = SchemePage(page).open(1).open_milestones()

    assert milestones_component.milestones.to_dicts() == [
        {"milestone": "Public consultation completed", "planned": "N/A", "actual": "N/A"},
        {"milestone": "Feasibility design completed", "planned": "N/A", "actual": "30/11/2020"},
        {"milestone": "Preliminary design completed", "planned": "N/A", "actual": "30/06/2022"},
        {"milestone": "Detailed design completed", "planned": "N/A", "actual": "30/06/2022"},
        {"milestone": "Construction started", "planned": "05/06/2023", "actual": "N/A"},
        {"milestone": "Construction completed", "planned": "31/08/2023", "actual": "N/A"},
    ]


@pytest.mark.usefixtures("live_server", "oidc_server")
def test_scheme_outputs(app_client: AppClient, oidc_client: OidcClient, page: Page) -> None:
    app_client.add_authorities(AuthorityRepr(id=1, name="Liverpool City Region Combined Authority"))
    app_client.add_users(1, UserRepr(email="boardman@example.com"))
    app_client.add_schemes(
        1,
        SchemeRepr(
            id=1,
            name="Wirral Package",
            output_revisions=[
                OutputRevisionRepr(
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    type="New segregated cycling facility",
                    measure="miles",
                    value="3.000000",
                    observation_type="Planned",
                ),
                OutputRevisionRepr(
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    type="New segregated cycling facility",
                    measure="miles",
                    value="2.000000",
                    observation_type="Actual",
                ),
                OutputRevisionRepr(
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    type="Improvements to make an existing walking/cycle route safer",
                    measure="number of junctions",
                    value="2.600000",
                    observation_type="Planned",
                ),
            ],
        ),
    )
    oidc_client.add_user(StubUser("boardman", "boardman@example.com"))

    outputs_component = SchemePage(page).open(1).open_outputs()

    assert outputs_component.outputs.to_dicts() == [
        {
            "infrastructure": "New segregated cycling facility",
            "measurement": "Miles",
            "planned": "3",
            "actual": "2",
            "planned_outputs_not_yet_delivered": "1",
            "output_delivery_status": "In progress",
        },
        {
            "infrastructure": "Improvements to make an existing walking/cycle route safer",
            "measurement": "Number of junctions",
            "planned": "2.6",
            "actual": "N/A",
            "planned_outputs_not_yet_delivered": "2.6",
            "output_delivery_status": "Not started",
        },
    ]
