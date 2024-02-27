from datetime import date, datetime
from decimal import Decimal
from typing import Any, Mapping

import pytest
from flask.testing import FlaskClient

from schemes.domain.authorities import Authority, AuthorityRepository
from schemes.domain.dates import DateRange
from schemes.domain.schemes import (
    AuthorityReview,
    DataSource,
    FinancialRevision,
    FinancialType,
    FundingProgramme,
    Milestone,
    MilestoneRevision,
    ObservationType,
    OutputRevision,
    OutputTypeMeasure,
    Scheme,
    SchemeRepository,
    SchemeType,
)
from schemes.domain.users import User, UserRepository
from schemes.infrastructure.clock import Clock
from tests.integration.pages import ChangeMilestoneDatesPage, SchemePage


class TestScheme:
    @pytest.fixture(name="auth", autouse=True)
    def auth_fixture(self, authorities: AuthorityRepository, users: UserRepository, client: FlaskClient) -> None:
        authorities.add(Authority(id_=1, name="Liverpool City Region Combined Authority"))
        users.add(User(email="boardman@example.com", authority_id=1))
        with client.session_transaction() as session:
            session["user"] = {"email": "boardman@example.com"}

    def test_scheme_shows_html(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))
        chromium_default_accept = (
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
        )

        response = client.get("/schemes/1", headers={"Accept": chromium_default_accept})

        assert response.status_code == 200 and response.content_type == "text/html; charset=utf-8"

    def test_scheme_shows_back(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        scheme_page = SchemePage.open(client, id_=1)

        assert scheme_page.back_url == "/schemes"

    def test_scheme_shows_authority(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        scheme_page = SchemePage.open(client, id_=1)

        assert scheme_page.authority == "Liverpool City Region Combined Authority"

    def test_scheme_shows_name(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        scheme_page = SchemePage.open(client, id_=1)

        assert scheme_page.name == "Wirral Package"

    @pytest.mark.parametrize(
        "review_date, expected_needs_review", [(datetime(2023, 1, 2), True), (datetime(2023, 4, 1), False)]
    )
    def test_scheme_shows_needs_review(
        self,
        clock: Clock,
        schemes: SchemeRepository,
        client: FlaskClient,
        review_date: datetime,
        expected_needs_review: bool,
    ) -> None:
        clock.now = datetime(2023, 4, 24)
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme.update_authority_review(AuthorityReview(id_=1, review_date=review_date, source=DataSource.ATF4_BID))
        schemes.add(scheme)

        scheme_page = SchemePage.open(client, id_=1)

        assert scheme_page.needs_review == expected_needs_review

    def test_scheme_shows_minimal_overview(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        scheme_page = SchemePage.open(client, id_=1)

        assert (
            scheme_page.overview.reference == "ATE00001"
            and scheme_page.overview.scheme_type == ""
            and scheme_page.overview.funding_programme == ""
            and scheme_page.overview.current_milestone == ""
            and scheme_page.overview.last_reviewed == ""
        )

    def test_scheme_shows_overview(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme.type = SchemeType.CONSTRUCTION
        scheme.funding_programme = FundingProgramme.ATF4
        scheme.update_authority_review(
            AuthorityReview(id_=1, review_date=datetime(2020, 1, 2), source=DataSource.ATF4_BID)
        )
        scheme.milestones.update_milestone(
            MilestoneRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 1),
                source=DataSource.ATF4_BID,
            )
        )
        schemes.add(scheme)

        scheme_page = SchemePage.open(client, id_=1)

        assert (
            scheme_page.overview.reference == "ATE00001"
            and scheme_page.overview.scheme_type == "Construction"
            and scheme_page.overview.funding_programme == "ATF4"
            and scheme_page.overview.current_milestone == "Detailed design completed"
            and scheme_page.overview.last_reviewed == "2 Jan 2020"
        )

    def test_scheme_shows_change_milestones(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        scheme_page = SchemePage.open(client, id_=1)

        assert scheme_page.milestones.change_milestones_url == "/schemes/1/milestones"

    def test_scheme_shows_minimal_milestones(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        scheme_page = SchemePage.open(client, id_=1)

        assert scheme_page.milestones.milestones.to_dicts() == [
            {"milestone": "Feasibility design completed", "planned": "", "actual": ""},
            {"milestone": "Preliminary design completed", "planned": "", "actual": ""},
            {"milestone": "Detailed design completed", "planned": "", "actual": ""},
            {"milestone": "Construction started", "planned": "", "actual": ""},
            {"milestone": "Construction completed", "planned": "", "actual": ""},
        ]

    def test_scheme_shows_milestones(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
        current = DateRange(datetime(2020, 1, 1), None)
        scheme.milestones.update_milestones(
            MilestoneRevision(
                1,
                current,
                Milestone.FEASIBILITY_DESIGN_COMPLETED,
                ObservationType.PLANNED,
                date(2020, 2, 1),
                DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                2,
                current,
                Milestone.FEASIBILITY_DESIGN_COMPLETED,
                ObservationType.ACTUAL,
                date(2020, 2, 2),
                DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                3,
                current,
                Milestone.PRELIMINARY_DESIGN_COMPLETED,
                ObservationType.PLANNED,
                date(2020, 3, 1),
                DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                4,
                current,
                Milestone.PRELIMINARY_DESIGN_COMPLETED,
                ObservationType.ACTUAL,
                date(2020, 3, 2),
                DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                5,
                current,
                Milestone.DETAILED_DESIGN_COMPLETED,
                ObservationType.PLANNED,
                date(2020, 4, 1),
                DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                6,
                current,
                Milestone.DETAILED_DESIGN_COMPLETED,
                ObservationType.ACTUAL,
                date(2020, 4, 2),
                DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                7,
                current,
                Milestone.CONSTRUCTION_STARTED,
                ObservationType.PLANNED,
                date(2020, 5, 1),
                DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                8,
                current,
                Milestone.CONSTRUCTION_STARTED,
                ObservationType.ACTUAL,
                date(2020, 5, 2),
                DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                9,
                current,
                Milestone.CONSTRUCTION_COMPLETED,
                ObservationType.PLANNED,
                date(2020, 6, 1),
                DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                10,
                current,
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

    def test_scheme_shows_minimal_outputs(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme.outputs.update_outputs(
            OutputRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_measure=OutputTypeMeasure.NEW_SEGREGATED_CYCLING_FACILITY_NUMBER_OF_JUNCTIONS,
                value=Decimal(1),
                observation_type=ObservationType.ACTUAL,
            )
        )
        schemes.add(scheme)

        scheme_page = SchemePage.open(client, id_=1)

        assert scheme_page.outputs.outputs
        outputs = list(scheme_page.outputs.outputs)
        assert outputs[0].planned == ""

    def test_scheme_shows_outputs(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme.outputs.update_outputs(
            OutputRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_measure=OutputTypeMeasure.NEW_SEGREGATED_CYCLING_FACILITY_MILES,
                value=Decimal("3.000000"),
                observation_type=ObservationType.PLANNED,
            ),
            OutputRevision(
                id_=2,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_NUMBER_OF_JUNCTIONS,
                value=Decimal("2.600000"),
                observation_type=ObservationType.PLANNED,
            ),
        )
        schemes.add(scheme)

        scheme_page = SchemePage.open(client, id_=1)

        assert scheme_page.outputs.outputs
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

    def test_scheme_shows_zero_outputs(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme.outputs.update_outputs(
            OutputRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_measure=OutputTypeMeasure.NEW_SEGREGATED_CYCLING_FACILITY_NUMBER_OF_JUNCTIONS,
                value=Decimal("0.000000"),
                observation_type=ObservationType.PLANNED,
            )
        )
        schemes.add(scheme)

        scheme_page = SchemePage.open(client, id_=1)

        assert scheme_page.outputs.outputs
        outputs = list(scheme_page.outputs.outputs)
        assert outputs[0].planned == "0"

    def test_scheme_shows_message_when_no_outputs(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        scheme_page = SchemePage.open(client, id_=1)

        assert not scheme_page.outputs.outputs
        assert scheme_page.outputs.is_no_outputs_message_visible

    def test_cannot_scheme_when_different_authority(
        self, authorities: AuthorityRepository, schemes: SchemeRepository, client: FlaskClient
    ) -> None:
        authorities.add(Authority(id_=2, name="West Yorkshire Combined Authority"))
        schemes.add(Scheme(id_=2, name="Hospital Fields Road", authority_id=2))

        forbidden_page = SchemePage.open_when_unauthorized(client, id_=2)

        assert forbidden_page.is_visible and forbidden_page.is_forbidden

    def test_milestones_form_shows_back(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        change_milestone_dates_page = ChangeMilestoneDatesPage.open(client, id_=1)

        assert change_milestone_dates_page.back_url == "/schemes/1"

    def test_milestones_form_shows_fields(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        change_milestone_dates_page = ChangeMilestoneDatesPage.open(client, id_=1)

        assert (
            change_milestone_dates_page.form.feasibility_design_completed.planned.name
            == "feasibility_design_completed_planned"
            and change_milestone_dates_page.form.feasibility_design_completed.actual.name
            == "feasibility_design_completed_actual"
            and change_milestone_dates_page.form.preliminary_design_completed.planned.name
            == "preliminary_design_completed_planned"
            and change_milestone_dates_page.form.preliminary_design_completed.actual.name
            == "preliminary_design_completed_actual"
            and change_milestone_dates_page.form.detailed_design_completed.planned.name
            == "detailed_design_completed_planned"
            and change_milestone_dates_page.form.detailed_design_completed.actual.name
            == "detailed_design_completed_actual"
            and change_milestone_dates_page.form.construction_started.planned.name == "construction_started_planned"
            and change_milestone_dates_page.form.construction_started.actual.name == "construction_started_actual"
            and change_milestone_dates_page.form.construction_completed.planned.name == "construction_completed_planned"
            and change_milestone_dates_page.form.construction_completed.actual.name == "construction_completed_actual"
        )

    def test_milestones_form_shows_date(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme.milestones.update_milestones(
            MilestoneRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1, 12), None),
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 2),
                source=DataSource.ATF4_BID,
            )
        )
        schemes.add(scheme)

        change_milestone_dates_page = ChangeMilestoneDatesPage.open(client, id_=1)

        assert change_milestone_dates_page.title == "Update your capital schemes - Active Travel England - GOV.UK"
        assert change_milestone_dates_page.form.construction_started.actual.value == "2 1 2020"

    def test_milestones_form_shows_confirm(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        change_milestone_dates_page = ChangeMilestoneDatesPage.open(client, id_=1)

        assert change_milestone_dates_page.form.confirm_url == "/schemes/1/milestones"

    def test_milestones_form_shows_cancel(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        change_milestone_dates_page = ChangeMilestoneDatesPage.open(client, id_=1)

        assert change_milestone_dates_page.form.cancel_url == "/schemes/1"

    def test_cannot_milestones_form_when_different_authority(
        self, authorities: AuthorityRepository, schemes: SchemeRepository, client: FlaskClient
    ) -> None:
        authorities.add(Authority(id_=2, name="West Yorkshire Combined Authority"))
        schemes.add(Scheme(id_=2, name="Hospital Fields Road", authority_id=2))

        forbidden_page = ChangeMilestoneDatesPage.open_when_unauthorized(client, id_=2)

        assert forbidden_page.is_visible and forbidden_page.is_forbidden

    def test_milestones_updates_milestones(
        self, clock: Clock, schemes: SchemeRepository, client: FlaskClient, csrf_token: str
    ) -> None:
        clock.now = datetime(2020, 1, 31, 13)
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme.milestones.update_milestones(
            MilestoneRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1, 12), None),
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 2),
                source=DataSource.ATF4_BID,
            )
        )
        schemes.add(scheme)

        client.post(
            "/schemes/1/milestones", data={"csrf_token": csrf_token, "construction_started_actual": ["3", "1", "2020"]}
        )

        actual_scheme = schemes.get(1)
        assert actual_scheme
        milestone_revision1: MilestoneRevision
        milestone_revision2: MilestoneRevision
        milestone_revision1, milestone_revision2 = actual_scheme.milestones.milestone_revisions
        assert milestone_revision1.id == 1 and milestone_revision1.effective.date_to == datetime(2020, 1, 31, 13)
        assert (
            milestone_revision2.effective == DateRange(datetime(2020, 1, 31, 13), None)
            and milestone_revision2.milestone == Milestone.CONSTRUCTION_STARTED
            and milestone_revision2.observation_type == ObservationType.ACTUAL
            and milestone_revision2.status_date == date(2020, 1, 3)
            and milestone_revision2.source == DataSource.AUTHORITY_UPDATE
        )

    def test_milestones_shows_scheme(self, schemes: SchemeRepository, client: FlaskClient, csrf_token: str) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        response = client.post("/schemes/1/milestones", data={"csrf_token": csrf_token})

        assert response.status_code == 302 and response.location == "/schemes/1"

    def test_cannot_milestones_when_error(
        self, schemes: SchemeRepository, client: FlaskClient, csrf_token: str
    ) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme.milestones.update_milestones(
            MilestoneRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1, 12), None),
                milestone=Milestone.CONSTRUCTION_STARTED,
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
                | {"csrf_token": csrf_token, "construction_started_actual": ["x", "x", "x"]},
            )
        )

        assert (
            change_milestone_dates_page.title == "Error: Update your capital schemes - Active Travel England - GOV.UK"
        )
        assert change_milestone_dates_page.errors and list(change_milestone_dates_page.errors) == [
            "Construction started actual date must be a real date"
        ]
        assert (
            change_milestone_dates_page.form.construction_started.actual.is_errored
            and change_milestone_dates_page.form.construction_started.actual.error
            == "Error: Construction started actual date must be a real date"
            and change_milestone_dates_page.form.construction_started.actual.value == "x x x"
        )
        actual_scheme = schemes.get(1)
        assert actual_scheme
        milestone_revision1: MilestoneRevision
        (milestone_revision1,) = actual_scheme.milestones.milestone_revisions
        assert (
            milestone_revision1.id == 1
            and milestone_revision1.effective == DateRange(datetime(2020, 1, 1, 12), None)
            and milestone_revision1.milestone == Milestone.CONSTRUCTION_STARTED
            and milestone_revision1.observation_type == ObservationType.ACTUAL
            and milestone_revision1.status_date == date(2020, 1, 2)
            and milestone_revision1.source == DataSource.ATF4_BID
        )

    def test_cannot_milestones_when_no_csrf_token(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        change_milestone_dates_page = ChangeMilestoneDatesPage(
            client.post("/schemes/1/milestones", follow_redirects=True)
        )

        assert change_milestone_dates_page.is_visible
        assert (
            change_milestone_dates_page.notification_banner
            and change_milestone_dates_page.notification_banner.heading
            == "The form you were submitting has expired. Please try again."
        )

    def test_cannot_milestones_when_incorrect_csrf_token(
        self, schemes: SchemeRepository, client: FlaskClient, csrf_token: str
    ) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        change_milestone_dates_page = ChangeMilestoneDatesPage(
            client.post("/schemes/1/milestones", data={"csrf_token": "x"}, follow_redirects=True)
        )

        assert change_milestone_dates_page.is_visible
        assert (
            change_milestone_dates_page.notification_banner
            and change_milestone_dates_page.notification_banner.heading
            == "The form you were submitting has expired. Please try again."
        )

    def test_cannot_milestones_when_different_authority(
        self, authorities: AuthorityRepository, schemes: SchemeRepository, client: FlaskClient, csrf_token: str
    ) -> None:
        authorities.add(Authority(id_=2, name="West Yorkshire Combined Authority"))
        schemes.add(Scheme(id_=2, name="Hospital Fields Road", authority_id=2))

        response = client.post("/schemes/2/milestones", data={"csrf_token": csrf_token})

        assert response.status_code == 403

    def empty_change_milestone_dates_form(self) -> dict[str, list[str]]:
        empty_date = ["", "", ""]
        return {
            "feasibility_design_completed_planned": empty_date,
            "feasibility_design_completed_actual": empty_date,
            "preliminary_design_completed_planned": empty_date,
            "preliminary_design_completed_actual": empty_date,
            "detailed_design_completed_planned": empty_date,
            "detailed_design_completed_actual": empty_date,
            "construction_started_planned": empty_date,
            "construction_started_actual": empty_date,
            "construction_completed_planned": empty_date,
            "construction_completed_actual": empty_date,
        }


class TestSchemeApi:
    @pytest.fixture(name="config", scope="class")
    def config_fixture(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        return dict(config) | {"API_KEY": "boardman"}

    def test_get_scheme(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme.type = SchemeType.CONSTRUCTION
        scheme.funding_programme = FundingProgramme.ATF4
        schemes.add(scheme)

        response = client.get("/schemes/1", headers={"Accept": "application/json", "Authorization": "API-Key boardman"})

        assert response.json == {
            "id": 1,
            "name": "Wirral Package",
            "type": "construction",
            "funding_programme": "ATF4",
            "authority_reviews": [],
            "financial_revisions": [],
            "milestone_revisions": [],
            "output_revisions": [],
        }

    def test_get_scheme_authority_reviews(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme.update_authority_review(
            AuthorityReview(id_=2, review_date=datetime(2020, 1, 1, 12), source=DataSource.ATF4_BID)
        )
        schemes.add(scheme)

        response = client.get("/schemes/1", headers={"Accept": "application/json", "Authorization": "API-Key boardman"})

        assert response.json and response.json["id"] == 1
        assert response.json["authority_reviews"] == [
            {
                "id": 2,
                "review_date": "2020-01-01T12:00:00",
                "source": "ATF4 Bid",
            }
        ]

    def test_get_scheme_financial_revisions(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme.funding.update_financial(
            FinancialRevision(
                id_=2,
                effective=DateRange(datetime(2020, 1, 1, 12), None),
                type_=FinancialType.FUNDING_ALLOCATION,
                amount=100_000,
                source=DataSource.ATF4_BID,
            )
        )
        schemes.add(scheme)

        response = client.get("/schemes/1", headers={"Accept": "application/json", "Authorization": "API-Key boardman"})

        assert response.json and response.json["id"] == 1
        assert response.json["financial_revisions"] == [
            {
                "id": 2,
                "effective_date_from": "2020-01-01T12:00:00",
                "effective_date_to": None,
                "type": "funding allocation",
                "amount": 100_000,
                "source": "ATF4 Bid",
            }
        ]

    def test_get_scheme_milestone_revisions(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme.milestones.update_milestone(
            MilestoneRevision(
                id_=2,
                effective=DateRange(datetime(2020, 1, 1, 12), None),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 1),
                source=DataSource.ATF4_BID,
            )
        )
        schemes.add(scheme)

        response = client.get("/schemes/1", headers={"Accept": "application/json", "Authorization": "API-Key boardman"})

        assert response.json and response.json["id"] == 1
        assert response.json["milestone_revisions"] == [
            {
                "id": 2,
                "effective_date_from": "2020-01-01T12:00:00",
                "effective_date_to": None,
                "milestone": "detailed design completed",
                "observation_type": "Actual",
                "status_date": "2020-01-01",
                "source": "ATF4 Bid",
            }
        ]

    def test_get_scheme_output_revisions(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme.outputs.update_output(
            OutputRevision(
                id_=2,
                effective=DateRange(datetime(2020, 1, 1, 12), None),
                type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
                value=Decimal(10),
                observation_type=ObservationType.ACTUAL,
            )
        )
        schemes.add(scheme)

        response = client.get("/schemes/1", headers={"Accept": "application/json", "Authorization": "API-Key boardman"})

        assert response.json and response.json["id"] == 1
        assert response.json["output_revisions"] == [
            {
                "id": 2,
                "effective_date_from": "2020-01-01T12:00:00",
                "effective_date_to": None,
                "type": "Improvements to make an existing walking/cycle route safer",
                "measure": "miles",
                "value": "10",
                "observation_type": "Actual",
            }
        ]

    def test_cannot_get_scheme_when_no_credentials(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        response = client.get("/schemes/1", headers={"Accept": "application/json"})

        assert response.status_code == 401

    def test_cannot_get_scheme_when_incorrect_credentials(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        response = client.get("/schemes/1", headers={"Accept": "application/json", "Authorization": "API-Key obree"})

        assert response.status_code == 401


class TestSchemeApiWhenDisabled:
    def test_cannot_get_scheme(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        response = client.get("/schemes/1", headers={"Accept": "application/json", "Authorization": "API-Key boardman"})

        assert response.status_code == 401
