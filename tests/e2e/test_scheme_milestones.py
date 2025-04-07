import pytest
from playwright.sync_api import Page

from tests.e2e.api_client import ApiClient
from tests.e2e.api_client import AuthorityRepr as ApiAuthorityRepr
from tests.e2e.app_client import (
    AppClient,
    AuthorityRepr,
    MilestoneRevisionRepr,
    UserRepr,
)
from tests.e2e.builders import build_scheme
from tests.e2e.oidc_server.users import StubUser
from tests.e2e.oidc_server.web_client import OidcClient
from tests.e2e.pages import SchemePage


@pytest.mark.usefixtures("live_server", "oidc_server")
def test_scheme_milestones(app_client: AppClient, api_client: ApiClient, oidc_client: OidcClient, page: Page) -> None:
    app_client.add_authorities(AuthorityRepr(abbreviation="LIV", name="Liverpool City Region Combined Authority"))
    api_client.add_authorities(
        ApiAuthorityRepr(abbreviation="LIV", fullName="Liverpool City Region Combined Authority")
    )
    app_client.add_users("LIV", UserRepr(email="boardman@example.com"))
    app_client.add_schemes(
        build_scheme(
            id_=1,
            reference="ATE00001",
            name="Wirral Package",
            authority_abbreviation="LIV",
            milestone_revisions=[
                MilestoneRevisionRepr(
                    id=1,
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    milestone="feasibility design completed",
                    observation_type="actual",
                    status_date="2020-11-30",
                    source="ATF4 bid",
                ),
                MilestoneRevisionRepr(
                    id=2,
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    milestone="preliminary design completed",
                    observation_type="actual",
                    status_date="2022-06-30",
                    source="ATF4 bid",
                ),
                MilestoneRevisionRepr(
                    id=3,
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    milestone="detailed design completed",
                    observation_type="actual",
                    status_date="2022-06-30",
                    source="ATF4 bid",
                ),
                MilestoneRevisionRepr(
                    id=4,
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    milestone="construction started",
                    observation_type="planned",
                    status_date="2023-06-05",
                    source="ATF4 bid",
                ),
                MilestoneRevisionRepr(
                    id=5,
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    milestone="construction completed",
                    observation_type="planned",
                    status_date="2023-08-31",
                    source="ATF4 bid",
                ),
            ],
        ),
    )
    oidc_client.add_user(StubUser("boardman", "boardman@example.com"))

    scheme_page = SchemePage.open(page, id_=1)

    assert scheme_page.milestones.milestones.to_dicts() == [
        {"milestone": "Feasibility design completed", "planned": "", "actual": "30 Nov 2020"},
        {"milestone": "Preliminary design completed", "planned": "", "actual": "30 Jun 2022"},
        {"milestone": "Detailed design completed", "planned": "", "actual": "30 Jun 2022"},
        {"milestone": "Construction started", "planned": "5 Jun 2023", "actual": ""},
        {"milestone": "Construction completed", "planned": "31 Aug 2023", "actual": ""},
    ]


@pytest.mark.usefixtures("live_server", "oidc_server")
def test_change_milestones(app_client: AppClient, api_client: ApiClient, oidc_client: OidcClient, page: Page) -> None:
    app_client.set_clock("2023-08-01T13:00:00")
    app_client.add_authorities(AuthorityRepr(abbreviation="LIV", name="Liverpool City Region Combined Authority"))
    api_client.add_authorities(
        ApiAuthorityRepr(abbreviation="LIV", fullName="Liverpool City Region Combined Authority")
    )
    app_client.add_users("LIV", UserRepr(email="boardman@example.com"))
    app_client.add_schemes(
        build_scheme(
            id_=1,
            reference="ATE00001",
            name="Wirral Package",
            authority_abbreviation="LIV",
            milestone_revisions=[
                MilestoneRevisionRepr(
                    id=1,
                    effective_date_from="2020-01-01T12:00:00",
                    effective_date_to=None,
                    milestone="feasibility design completed",
                    observation_type="actual",
                    status_date="2020-11-30",
                    source="ATF4 bid",
                ),
                MilestoneRevisionRepr(
                    id=2,
                    effective_date_from="2020-01-01T12:00:00",
                    effective_date_to=None,
                    milestone="preliminary design completed",
                    observation_type="actual",
                    status_date="2022-06-30",
                    source="ATF4 bid",
                ),
                MilestoneRevisionRepr(
                    id=3,
                    effective_date_from="2020-01-01T12:00:00",
                    effective_date_to=None,
                    milestone="detailed design completed",
                    observation_type="actual",
                    status_date="2022-06-30",
                    source="ATF4 bid",
                ),
                MilestoneRevisionRepr(
                    id=4,
                    effective_date_from="2020-01-01T12:00:00",
                    effective_date_to=None,
                    milestone="construction started",
                    observation_type="planned",
                    status_date="2023-06-05",
                    source="ATF4 bid",
                ),
                MilestoneRevisionRepr(
                    id=5,
                    effective_date_from="2020-01-01T12:00:00",
                    effective_date_to=None,
                    milestone="construction completed",
                    observation_type="planned",
                    status_date="2023-08-31",
                    source="ATF4 bid",
                ),
            ],
        ),
    )
    oidc_client.add_user(StubUser("boardman", "boardman@example.com"))

    scheme_page = (
        SchemePage.open(page, id_=1)
        .milestones.change_milestone_dates()
        .form.enter_construction_started_actual("5 7 2023")
        .enter_construction_completed_planned("30 9 2023")
        .confirm()
    )

    assert scheme_page.heading.text == "Wirral Package"
    assert (
        scheme_page.milestones.milestones["Construction started"].actual == "5 Jul 2023"
        and scheme_page.milestones.milestones["Construction completed"].planned == "30 Sep 2023"
    )
    assert app_client.get_scheme(id_=1).milestone_revisions == [
        MilestoneRevisionRepr(
            id=1,
            effective_date_from="2020-01-01T12:00:00",
            effective_date_to=None,
            milestone="feasibility design completed",
            observation_type="actual",
            status_date="2020-11-30",
            source="ATF4 bid",
        ),
        MilestoneRevisionRepr(
            id=2,
            effective_date_from="2020-01-01T12:00:00",
            effective_date_to=None,
            milestone="preliminary design completed",
            observation_type="actual",
            status_date="2022-06-30",
            source="ATF4 bid",
        ),
        MilestoneRevisionRepr(
            id=3,
            effective_date_from="2020-01-01T12:00:00",
            effective_date_to=None,
            milestone="detailed design completed",
            observation_type="actual",
            status_date="2022-06-30",
            source="ATF4 bid",
        ),
        MilestoneRevisionRepr(
            id=4,
            effective_date_from="2020-01-01T12:00:00",
            effective_date_to=None,
            milestone="construction started",
            observation_type="planned",
            status_date="2023-06-05",
            source="ATF4 bid",
        ),
        MilestoneRevisionRepr(
            id=5,
            effective_date_from="2020-01-01T12:00:00",
            effective_date_to="2023-08-01T13:00:00",
            milestone="construction completed",
            observation_type="planned",
            status_date="2023-08-31",
            source="ATF4 bid",
        ),
        MilestoneRevisionRepr(
            id=6,
            effective_date_from="2023-08-01T13:00:00",
            effective_date_to=None,
            milestone="construction started",
            observation_type="actual",
            status_date="2023-07-05",
            source="authority update",
        ),
        MilestoneRevisionRepr(
            id=7,
            effective_date_from="2023-08-01T13:00:00",
            effective_date_to=None,
            milestone="construction completed",
            observation_type="planned",
            status_date="2023-09-30",
            source="authority update",
        ),
    ]


@pytest.mark.usefixtures("live_server", "oidc_server")
def test_cannot_change_milestones_when_error(
    app_client: AppClient, api_client: ApiClient, oidc_client: OidcClient, page: Page
) -> None:
    app_client.add_authorities(AuthorityRepr(abbreviation="LIV", name="Liverpool City Region Combined Authority"))
    api_client.add_authorities(
        ApiAuthorityRepr(abbreviation="LIV", fullName="Liverpool City Region Combined Authority")
    )
    app_client.add_users("LIV", UserRepr(email="boardman@example.com"))
    app_client.add_schemes(
        build_scheme(
            id_=1,
            reference="ATE00001",
            name="Wirral Package",
            authority_abbreviation="LIV",
            milestone_revisions=[
                MilestoneRevisionRepr(
                    id=1,
                    effective_date_from="2020-01-01T12:00:00",
                    effective_date_to=None,
                    milestone="feasibility design completed",
                    observation_type="actual",
                    status_date="2020-11-30",
                    source="ATF4 bid",
                ),
                MilestoneRevisionRepr(
                    id=2,
                    effective_date_from="2020-01-01T12:00:00",
                    effective_date_to=None,
                    milestone="preliminary design completed",
                    observation_type="actual",
                    status_date="2022-06-30",
                    source="ATF4 bid",
                ),
                MilestoneRevisionRepr(
                    id=3,
                    effective_date_from="2020-01-01T12:00:00",
                    effective_date_to=None,
                    milestone="detailed design completed",
                    observation_type="actual",
                    status_date="2022-06-30",
                    source="ATF4 bid",
                ),
                MilestoneRevisionRepr(
                    id=4,
                    effective_date_from="2020-01-01T12:00:00",
                    effective_date_to=None,
                    milestone="construction started",
                    observation_type="planned",
                    status_date="2023-06-05",
                    source="ATF4 bid",
                ),
                MilestoneRevisionRepr(
                    id=5,
                    effective_date_from="2020-01-01T12:00:00",
                    effective_date_to=None,
                    milestone="construction completed",
                    observation_type="planned",
                    status_date="2023-08-31",
                    source="ATF4 bid",
                ),
            ],
        ),
    )
    oidc_client.add_user(StubUser("boardman", "boardman@example.com"))

    change_milestone_page = (
        SchemePage.open(page, id_=1)
        .milestones.change_milestone_dates()
        .form.enter_construction_completed_planned("x x x")
        .confirm_when_error()
    )

    assert (
        change_milestone_page.title
        == "Error: Change milestone dates - Update your capital schemes - Active Travel England - GOV.UK"
    )
    assert list(change_milestone_page.errors) == ["Construction completed planned date must be a real date"]
    assert (
        change_milestone_page.form.construction_completed_planned.is_errored
        and change_milestone_page.form.construction_completed_planned.error
        == "Error: Construction completed planned date must be a real date"
        and change_milestone_page.form.construction_completed_planned.value == "x x x"
    )

    assert app_client.get_scheme(id_=1).milestone_revisions == [
        MilestoneRevisionRepr(
            id=1,
            effective_date_from="2020-01-01T12:00:00",
            effective_date_to=None,
            milestone="feasibility design completed",
            observation_type="actual",
            status_date="2020-11-30",
            source="ATF4 bid",
        ),
        MilestoneRevisionRepr(
            id=2,
            effective_date_from="2020-01-01T12:00:00",
            effective_date_to=None,
            milestone="preliminary design completed",
            observation_type="actual",
            status_date="2022-06-30",
            source="ATF4 bid",
        ),
        MilestoneRevisionRepr(
            id=3,
            effective_date_from="2020-01-01T12:00:00",
            effective_date_to=None,
            milestone="detailed design completed",
            observation_type="actual",
            status_date="2022-06-30",
            source="ATF4 bid",
        ),
        MilestoneRevisionRepr(
            id=4,
            effective_date_from="2020-01-01T12:00:00",
            effective_date_to=None,
            milestone="construction started",
            observation_type="planned",
            status_date="2023-06-05",
            source="ATF4 bid",
        ),
        MilestoneRevisionRepr(
            id=5,
            effective_date_from="2020-01-01T12:00:00",
            effective_date_to=None,
            milestone="construction completed",
            observation_type="planned",
            status_date="2023-08-31",
            source="ATF4 bid",
        ),
    ]
