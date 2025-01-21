from datetime import date, datetime

import pytest
from flask.testing import FlaskClient

from schemes.domain.authorities import Authority, AuthorityRepository
from schemes.domain.dates import DateRange
from schemes.domain.schemes import (
    BidStatus,
    DataSource,
    Milestone,
    MilestoneRevision,
    ObservationType,
    SchemeRepository,
    SchemeType,
)
from schemes.domain.users import User, UserRepository
from schemes.infrastructure.clock import Clock
from tests.builders import build_scheme
from tests.integration.pages import ChangeMilestoneDatesPage, SchemePage


class TestSchemeMilestones:
    @pytest.fixture(name="auth", autouse=True)
    def auth_fixture(self, authorities: AuthorityRepository, users: UserRepository, client: FlaskClient) -> None:
        authorities.add(Authority(id_=1, name="Liverpool City Region Combined Authority"))
        users.add(User(email="boardman@example.com", authority_id=1))
        with client.session_transaction() as session:
            session["user"] = {"email": "boardman@example.com"}

    def test_scheme_shows_change_milestones(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_id=1))

        scheme_page = SchemePage.open(client, id_=1)

        assert scheme_page.milestones.change_milestones_url == "/schemes/1/milestones"

    def test_scheme_shows_minimal_milestones(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_id=1))

        scheme_page = SchemePage.open(client, id_=1)

        assert scheme_page.milestones.milestones.to_dicts() == [
            {"milestone": "Feasibility design completed", "planned": "", "actual": ""},
            {"milestone": "Preliminary design completed", "planned": "", "actual": ""},
            {"milestone": "Detailed design completed", "planned": "", "actual": ""},
            {"milestone": "Construction started", "planned": "", "actual": ""},
            {"milestone": "Construction completed", "planned": "", "actual": ""},
        ]

    def test_scheme_shows_development_milestones(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        scheme = build_scheme(
            id_=1, reference="ATE00001", name="Wirral Package", authority_id=1, type_=SchemeType.DEVELOPMENT
        )
        scheme.milestones.update_milestones(
            MilestoneRevision(
                1,
                DateRange(datetime(2020, 1, 1), None),
                Milestone.FEASIBILITY_DESIGN_COMPLETED,
                ObservationType.PLANNED,
                date(2020, 2, 1),
                DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                2,
                DateRange(datetime(2020, 1, 1), None),
                Milestone.FEASIBILITY_DESIGN_COMPLETED,
                ObservationType.ACTUAL,
                date(2020, 2, 2),
                DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                3,
                DateRange(datetime(2020, 1, 1), None),
                Milestone.PRELIMINARY_DESIGN_COMPLETED,
                ObservationType.PLANNED,
                date(2020, 3, 1),
                DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                4,
                DateRange(datetime(2020, 1, 1), None),
                Milestone.PRELIMINARY_DESIGN_COMPLETED,
                ObservationType.ACTUAL,
                date(2020, 3, 2),
                DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                5,
                DateRange(datetime(2020, 1, 1), None),
                Milestone.DETAILED_DESIGN_COMPLETED,
                ObservationType.PLANNED,
                date(2020, 4, 1),
                DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                6,
                DateRange(datetime(2020, 1, 1), None),
                Milestone.DETAILED_DESIGN_COMPLETED,
                ObservationType.ACTUAL,
                date(2020, 4, 2),
                DataSource.ATF4_BID,
            ),
        )
        schemes.add(scheme)

        scheme_page = SchemePage.open(client, id_=1)

        assert scheme_page.milestones.milestones.to_dicts() == [
            {"milestone": "Feasibility design completed", "planned": "1 Feb 2020", "actual": "2 Feb 2020"},
            {"milestone": "Preliminary design completed", "planned": "1 Mar 2020", "actual": "2 Mar 2020"},
            {"milestone": "Detailed design completed", "planned": "1 Apr 2020", "actual": "2 Apr 2020"},
        ]

    def test_scheme_shows_construction_milestones(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        scheme = build_scheme(
            id_=1, reference="ATE00001", name="Wirral Package", authority_id=1, type_=SchemeType.CONSTRUCTION
        )
        scheme.milestones.update_milestones(
            MilestoneRevision(
                1,
                DateRange(datetime(2020, 1, 1), None),
                Milestone.FEASIBILITY_DESIGN_COMPLETED,
                ObservationType.PLANNED,
                date(2020, 2, 1),
                DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                2,
                DateRange(datetime(2020, 1, 1), None),
                Milestone.FEASIBILITY_DESIGN_COMPLETED,
                ObservationType.ACTUAL,
                date(2020, 2, 2),
                DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                3,
                DateRange(datetime(2020, 1, 1), None),
                Milestone.PRELIMINARY_DESIGN_COMPLETED,
                ObservationType.PLANNED,
                date(2020, 3, 1),
                DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                4,
                DateRange(datetime(2020, 1, 1), None),
                Milestone.PRELIMINARY_DESIGN_COMPLETED,
                ObservationType.ACTUAL,
                date(2020, 3, 2),
                DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                5,
                DateRange(datetime(2020, 1, 1), None),
                Milestone.DETAILED_DESIGN_COMPLETED,
                ObservationType.PLANNED,
                date(2020, 4, 1),
                DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                6,
                DateRange(datetime(2020, 1, 1), None),
                Milestone.DETAILED_DESIGN_COMPLETED,
                ObservationType.ACTUAL,
                date(2020, 4, 2),
                DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                7,
                DateRange(datetime(2020, 1, 1), None),
                Milestone.CONSTRUCTION_STARTED,
                ObservationType.PLANNED,
                date(2020, 5, 1),
                DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                8,
                DateRange(datetime(2020, 1, 1), None),
                Milestone.CONSTRUCTION_STARTED,
                ObservationType.ACTUAL,
                date(2020, 5, 2),
                DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                9,
                DateRange(datetime(2020, 1, 1), None),
                Milestone.CONSTRUCTION_COMPLETED,
                ObservationType.PLANNED,
                date(2020, 6, 1),
                DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                10,
                DateRange(datetime(2020, 1, 1), None),
                Milestone.CONSTRUCTION_COMPLETED,
                ObservationType.ACTUAL,
                date(2020, 6, 2),
                DataSource.ATF4_BID,
            ),
        )
        schemes.add(scheme)

        scheme_page = SchemePage.open(client, id_=1)

        assert scheme_page.milestones.milestones.to_dicts() == [
            {"milestone": "Feasibility design completed", "planned": "1 Feb 2020", "actual": "2 Feb 2020"},
            {"milestone": "Preliminary design completed", "planned": "1 Mar 2020", "actual": "2 Mar 2020"},
            {"milestone": "Detailed design completed", "planned": "1 Apr 2020", "actual": "2 Apr 2020"},
            {"milestone": "Construction started", "planned": "1 May 2020", "actual": "2 May 2020"},
            {"milestone": "Construction completed", "planned": "1 Jun 2020", "actual": "2 Jun 2020"},
        ]

    def test_milestones_form_shows_title(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_id=1))

        change_milestone_dates_page = ChangeMilestoneDatesPage.open(client, id_=1)

        assert (
            change_milestone_dates_page.title
            == "Change milestone dates - Update your capital schemes - Active Travel England - GOV.UK"
        )

    def test_milestones_form_shows_back(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_id=1))

        change_milestone_dates_page = ChangeMilestoneDatesPage.open(client, id_=1)

        assert change_milestone_dates_page.back_url == "/schemes/1"

    def test_milestones_form_shows_scheme(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_id=1))

        change_milestone_dates_page = ChangeMilestoneDatesPage.open(client, id_=1)

        assert change_milestone_dates_page.heading and change_milestone_dates_page.heading.caption == "Wirral Package"

    def test_milestones_form_shows_fields(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(
            build_scheme(
                id_=1, reference="ATE00001", name="Wirral Package", authority_id=1, type_=SchemeType.CONSTRUCTION
            )
        )

        change_milestone_dates_page = ChangeMilestoneDatesPage.open(client, id_=1)

        assert (
            change_milestone_dates_page.form.feasibility_design_completed_planned.name
            == "feasibility_design_completed-planned"
            and change_milestone_dates_page.form.feasibility_design_completed_actual.name
            == "feasibility_design_completed-actual"
            and change_milestone_dates_page.form.preliminary_design_completed_planned.name
            == "preliminary_design_completed-planned"
            and change_milestone_dates_page.form.preliminary_design_completed_actual.name
            == "preliminary_design_completed-actual"
            and change_milestone_dates_page.form.detailed_design_completed_planned.name
            == "detailed_design_completed-planned"
            and change_milestone_dates_page.form.detailed_design_completed_actual.name
            == "detailed_design_completed-actual"
            and change_milestone_dates_page.form.construction_started_planned.name == "construction_started-planned"
            and change_milestone_dates_page.form.construction_started_actual.name == "construction_started-actual"
            and change_milestone_dates_page.form.construction_completed_planned.name == "construction_completed-planned"
            and change_milestone_dates_page.form.construction_completed_actual.name == "construction_completed-actual"
        )

    def test_milestones_form_shows_milestone_heading(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_id=1))

        change_milestone_dates_page = ChangeMilestoneDatesPage.open(client, id_=1)

        assert change_milestone_dates_page.form.detailed_design_completed_heading == "Detailed design completed"

    def test_milestones_form_shows_date(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        scheme = build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_id=1)
        scheme.milestones.update_milestones(
            MilestoneRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1, 12), None),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 2),
                source=DataSource.ATF4_BID,
            )
        )
        schemes.add(scheme)

        change_milestone_dates_page = ChangeMilestoneDatesPage.open(client, id_=1)

        assert change_milestone_dates_page.form.detailed_design_completed_actual.value == "2 1 2020"

    def test_milestones_form_shows_confirm(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_id=1))

        change_milestone_dates_page = ChangeMilestoneDatesPage.open(client, id_=1)

        assert change_milestone_dates_page.form.confirm_url == "/schemes/1/milestones"

    def test_milestones_form_shows_cancel(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_id=1))

        change_milestone_dates_page = ChangeMilestoneDatesPage.open(client, id_=1)

        assert change_milestone_dates_page.form.cancel_url == "/schemes/1"

    def test_cannot_milestones_form_when_different_authority(
        self, authorities: AuthorityRepository, schemes: SchemeRepository, client: FlaskClient
    ) -> None:
        authorities.add(Authority(id_=2, name="West Yorkshire Combined Authority"))
        schemes.add(build_scheme(id_=2, reference="ATE00002", name="Hospital Fields Road", authority_id=2))

        forbidden_page = ChangeMilestoneDatesPage.open_when_unauthorized(client, id_=2)

        assert forbidden_page.is_visible and forbidden_page.is_forbidden

    def test_cannot_milestones_form_when_no_authority(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(build_scheme(id_=2, reference="ATE00002", overview_revisions=[]))

        forbidden_page = ChangeMilestoneDatesPage.open_when_unauthorized(client, id_=2)

        assert forbidden_page.is_visible and forbidden_page.is_forbidden

    def test_cannot_milestones_form_when_unknown_scheme(self, client: FlaskClient) -> None:
        not_found_page = ChangeMilestoneDatesPage.open_when_not_found(client, id_=1)

        assert not_found_page.is_visible and not_found_page.is_not_found

    def test_cannot_milestones_form_when_not_updateable_scheme(
        self, schemes: SchemeRepository, client: FlaskClient
    ) -> None:
        schemes.add(
            build_scheme(
                id_=1, reference="ATE00001", name="Wirral Package", authority_id=1, bid_status=BidStatus.SUBMITTED
            )
        )

        not_found_page = ChangeMilestoneDatesPage.open_when_not_found(client, id_=1)

        assert not_found_page.is_visible and not_found_page.is_not_found

    @pytest.mark.parametrize("scheme_type", [SchemeType.DEVELOPMENT, SchemeType.CONSTRUCTION])
    def test_milestones_updates_milestones(
        self, clock: Clock, schemes: SchemeRepository, client: FlaskClient, csrf_token: str, scheme_type: SchemeType
    ) -> None:
        clock.now = datetime(2020, 2, 1, 13)
        scheme = build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_id=1, type_=scheme_type)
        scheme.milestones.update_milestones(
            MilestoneRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1, 12), None),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 2),
                source=DataSource.ATF4_BID,
            )
        )
        schemes.add(scheme)

        client.post(
            "/schemes/1/milestones",
            data={"csrf_token": csrf_token, "detailed_design_completed-actual": ["3", "1", "2020"]},
        )

        actual_scheme = schemes.get(1)
        assert actual_scheme
        milestone_revision1: MilestoneRevision
        milestone_revision2: MilestoneRevision
        milestone_revision1, milestone_revision2 = actual_scheme.milestones.milestone_revisions
        assert milestone_revision1.id == 1 and milestone_revision1.effective.date_to == datetime(2020, 2, 1, 13)
        assert (
            milestone_revision2.effective == DateRange(datetime(2020, 2, 1, 13), None)
            and milestone_revision2.milestone == Milestone.DETAILED_DESIGN_COMPLETED
            and milestone_revision2.observation_type == ObservationType.ACTUAL
            and milestone_revision2.status_date == date(2020, 1, 3)
            and milestone_revision2.source == DataSource.AUTHORITY_UPDATE
        )

    def test_milestones_shows_scheme(self, schemes: SchemeRepository, client: FlaskClient, csrf_token: str) -> None:
        schemes.add(build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_id=1))

        response = client.post("/schemes/1/milestones", data={"csrf_token": csrf_token})

        assert response.status_code == 302 and response.location == "/schemes/1"

    def test_cannot_milestones_when_error(
        self, schemes: SchemeRepository, client: FlaskClient, csrf_token: str
    ) -> None:
        scheme = build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_id=1)
        scheme.milestones.update_milestones(
            MilestoneRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1, 12), None),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 2),
                source=DataSource.ATF4_BID,
            )
        )
        schemes.add(scheme)

        change_milestone_dates_page = ChangeMilestoneDatesPage(
            client.post(
                "/schemes/1/milestones",
                data=self.empty_change_milestone_dates_form()
                | {"csrf_token": csrf_token, "detailed_design_completed-actual": ["x", "x", "x"]},
            )
        )

        assert (
            change_milestone_dates_page.title
            == "Error: Change milestone dates - Update your capital schemes - Active Travel England - GOV.UK"
        )
        assert change_milestone_dates_page.errors and list(change_milestone_dates_page.errors) == [
            "Detailed design completed actual date must be a real date"
        ]
        assert (
            change_milestone_dates_page.form.detailed_design_completed_actual.is_errored
            and change_milestone_dates_page.form.detailed_design_completed_actual.error
            == "Error: Detailed design completed actual date must be a real date"
            and change_milestone_dates_page.form.detailed_design_completed_actual.value == "x x x"
        )
        actual_scheme = schemes.get(1)
        assert actual_scheme
        milestone_revision1: MilestoneRevision
        (milestone_revision1,) = actual_scheme.milestones.milestone_revisions
        assert (
            milestone_revision1.id == 1
            and milestone_revision1.effective == DateRange(datetime(2020, 1, 1, 12), None)
            and milestone_revision1.milestone == Milestone.DETAILED_DESIGN_COMPLETED
            and milestone_revision1.observation_type == ObservationType.ACTUAL
            and milestone_revision1.status_date == date(2020, 1, 2)
            and milestone_revision1.source == DataSource.ATF4_BID
        )

    def test_cannot_milestones_when_no_csrf_token(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_id=1))

        change_milestone_dates_page = ChangeMilestoneDatesPage(
            client.post("/schemes/1/milestones", follow_redirects=True)
        )

        assert change_milestone_dates_page.is_visible
        assert (
            change_milestone_dates_page.important_notification
            and change_milestone_dates_page.important_notification.heading
            == "The form you were submitting has expired. Please try again."
        )

    def test_cannot_milestones_when_incorrect_csrf_token(
        self, schemes: SchemeRepository, client: FlaskClient, csrf_token: str
    ) -> None:
        schemes.add(build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_id=1))

        change_milestone_dates_page = ChangeMilestoneDatesPage(
            client.post("/schemes/1/milestones", data={"csrf_token": "x"}, follow_redirects=True)
        )

        assert change_milestone_dates_page.is_visible
        assert (
            change_milestone_dates_page.important_notification
            and change_milestone_dates_page.important_notification.heading
            == "The form you were submitting has expired. Please try again."
        )

    def test_cannot_milestones_when_different_authority(
        self, authorities: AuthorityRepository, schemes: SchemeRepository, client: FlaskClient, csrf_token: str
    ) -> None:
        authorities.add(Authority(id_=2, name="West Yorkshire Combined Authority"))
        schemes.add(build_scheme(id_=2, reference="ATE00002", name="Hospital Fields Road", authority_id=2))

        response = client.post("/schemes/2/milestones", data={"csrf_token": csrf_token})

        assert response.status_code == 403

    def test_cannot_milestones_when_no_authority(
        self, schemes: SchemeRepository, client: FlaskClient, csrf_token: str
    ) -> None:
        schemes.add(build_scheme(id_=2, reference="ATE00002", overview_revisions=[]))

        response = client.post("/schemes/2/milestones", data={"csrf_token": csrf_token})

        assert response.status_code == 403

    def test_cannot_milestones_when_unknown_scheme(self, client: FlaskClient, csrf_token: str) -> None:
        response = client.post("/schemes/1/milestones", data={"csrf_token": csrf_token})

        assert response.status_code == 404

    def test_cannot_milestones_when_not_updateable_scheme(
        self, schemes: SchemeRepository, client: FlaskClient, csrf_token: str
    ) -> None:
        schemes.add(
            build_scheme(
                id_=1, reference="ATE00001", name="Wirral Package", authority_id=1, bid_status=BidStatus.SUBMITTED
            )
        )

        response = client.post("/schemes/1/milestones", data={"csrf_token": csrf_token})

        assert response.status_code == 404

    def empty_change_milestone_dates_form(self) -> dict[str, list[str]]:
        empty_date = ["", "", ""]
        return {
            "feasibility_design_completed-planned": empty_date,
            "feasibility_design_completed-actual": empty_date,
            "preliminary_design_completed-planned": empty_date,
            "preliminary_design_completed-actual": empty_date,
            "detailed_design_completed-planned": empty_date,
            "detailed_design_completed-actual": empty_date,
            "construction_started-planned": empty_date,
            "construction_started-actual": empty_date,
            "construction_completed-planned": empty_date,
            "construction_completed-actual": empty_date,
        }
