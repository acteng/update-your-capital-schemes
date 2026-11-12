from datetime import date, datetime

import pytest
from flask.testing import FlaskClient

from schemes.domain.authorities import Authority, AuthorityRepository
from schemes.domain.schemes.data_sources import DataSource
from schemes.domain.schemes.milestones import Milestone, SchemeMilestone
from schemes.domain.schemes.observations import ObservationType
from schemes.domain.schemes.schemes import SchemeRepository, Status
from schemes.domain.users import User, UserRepository
from schemes.infrastructure.clock import Clock
from tests.integration.conftest import AsyncFlaskClient
from tests.integration.pages import ChangeMilestoneDatesPage, SchemePage
from tests.unit.domain.builders import build_scheme, build_scheme_funding, build_scheme_overview


class TestSchemeMilestones:
    @pytest.fixture(name="auth", autouse=True)
    async def auth_fixture(self, authorities: AuthorityRepository, users: UserRepository, client: FlaskClient) -> None:
        await authorities.add(Authority(abbreviation="LIV", name="Liverpool City Region Combined Authority"))
        users.add(User(email="boardman@example.com", authority_abbreviation="LIV"))
        with client.session_transaction() as session:
            session["user"] = {"email": "boardman@example.com"}

    async def test_scheme_shows_change_milestones(
        self, schemes: SchemeRepository, async_client: AsyncFlaskClient
    ) -> None:
        scheme = build_scheme(
            reference="ATE00001", overview=build_scheme_overview(name="Wirral Package", authority_abbreviation="LIV")
        )
        scheme.financials.update_funding(build_scheme_funding())
        await schemes.add(scheme)

        scheme_page = await SchemePage.open(async_client, reference="ATE00001")

        assert scheme_page.milestones.change_milestones_url == "/schemes/ATE00001/milestones"

    async def test_scheme_shows_minimal_milestones(
        self, schemes: SchemeRepository, async_client: AsyncFlaskClient
    ) -> None:
        scheme = build_scheme(
            reference="ATE00001", overview=build_scheme_overview(name="Wirral Package", authority_abbreviation="LIV")
        )
        scheme.financials.update_funding(build_scheme_funding())
        await schemes.add(scheme)

        scheme_page = await SchemePage.open(async_client, reference="ATE00001")

        assert scheme_page.milestones.milestones.to_dicts() == [
            {"milestone": "Feasibility design completed", "planned": "", "actual": ""},
            {"milestone": "Preliminary design completed", "planned": "", "actual": ""},
            {"milestone": "Detailed design completed", "planned": "", "actual": ""},
            {"milestone": "Construction started", "planned": "", "actual": ""},
            {"milestone": "Construction completed", "planned": "", "actual": ""},
        ]

    async def test_scheme_shows_milestones(self, schemes: SchemeRepository, async_client: AsyncFlaskClient) -> None:
        scheme = build_scheme(
            reference="ATE00001", overview=build_scheme_overview(name="Wirral Package", authority_abbreviation="LIV")
        )
        scheme.financials.update_funding(build_scheme_funding())
        scheme.milestones.update_milestones(
            SchemeMilestone(
                1,
                Milestone.FEASIBILITY_DESIGN_COMPLETED,
                ObservationType.PLANNED,
                date(2020, 2, 1),
                DataSource.ATF4_BID,
            ),
            SchemeMilestone(
                2,
                Milestone.FEASIBILITY_DESIGN_COMPLETED,
                ObservationType.ACTUAL,
                date(2020, 2, 2),
                DataSource.ATF4_BID,
            ),
            SchemeMilestone(
                3,
                Milestone.PRELIMINARY_DESIGN_COMPLETED,
                ObservationType.PLANNED,
                date(2020, 3, 1),
                DataSource.ATF4_BID,
            ),
            SchemeMilestone(
                4,
                Milestone.PRELIMINARY_DESIGN_COMPLETED,
                ObservationType.ACTUAL,
                date(2020, 3, 2),
                DataSource.ATF4_BID,
            ),
            SchemeMilestone(
                5,
                Milestone.DETAILED_DESIGN_COMPLETED,
                ObservationType.PLANNED,
                date(2020, 4, 1),
                DataSource.ATF4_BID,
            ),
            SchemeMilestone(
                6,
                Milestone.DETAILED_DESIGN_COMPLETED,
                ObservationType.ACTUAL,
                date(2020, 4, 2),
                DataSource.ATF4_BID,
            ),
            SchemeMilestone(
                7,
                Milestone.CONSTRUCTION_STARTED,
                ObservationType.PLANNED,
                date(2020, 5, 1),
                DataSource.ATF4_BID,
            ),
            SchemeMilestone(
                8,
                Milestone.CONSTRUCTION_STARTED,
                ObservationType.ACTUAL,
                date(2020, 5, 2),
                DataSource.ATF4_BID,
            ),
            SchemeMilestone(
                9,
                Milestone.CONSTRUCTION_COMPLETED,
                ObservationType.PLANNED,
                date(2020, 6, 1),
                DataSource.ATF4_BID,
            ),
            SchemeMilestone(
                10,
                Milestone.CONSTRUCTION_COMPLETED,
                ObservationType.ACTUAL,
                date(2020, 6, 2),
                DataSource.ATF4_BID,
            ),
        )
        await schemes.add(scheme)

        scheme_page = await SchemePage.open(async_client, reference="ATE00001")

        assert scheme_page.milestones.milestones.to_dicts() == [
            {"milestone": "Feasibility design completed", "planned": "1 Feb 2020", "actual": "2 Feb 2020"},
            {"milestone": "Preliminary design completed", "planned": "1 Mar 2020", "actual": "2 Mar 2020"},
            {"milestone": "Detailed design completed", "planned": "1 Apr 2020", "actual": "2 Apr 2020"},
            {"milestone": "Construction started", "planned": "1 May 2020", "actual": "2 May 2020"},
            {"milestone": "Construction completed", "planned": "1 Jun 2020", "actual": "2 Jun 2020"},
        ]

    async def test_milestones_form_shows_title(self, schemes: SchemeRepository, async_client: AsyncFlaskClient) -> None:
        scheme = build_scheme(
            reference="ATE00001", overview=build_scheme_overview(name="Wirral Package", authority_abbreviation="LIV")
        )
        scheme.financials.update_funding(build_scheme_funding())
        await schemes.add(scheme)

        change_milestone_dates_page = await ChangeMilestoneDatesPage.open(async_client, reference="ATE00001")

        assert (
            change_milestone_dates_page.title
            == "Change milestone dates - Update your capital schemes - Active Travel England - GOV.UK"
        )

    async def test_milestones_form_shows_back(self, schemes: SchemeRepository, async_client: AsyncFlaskClient) -> None:
        scheme = build_scheme(
            reference="ATE00001", overview=build_scheme_overview(name="Wirral Package", authority_abbreviation="LIV")
        )
        scheme.financials.update_funding(build_scheme_funding())
        await schemes.add(scheme)

        change_milestone_dates_page = await ChangeMilestoneDatesPage.open(async_client, reference="ATE00001")

        assert change_milestone_dates_page.back_url == "/schemes/ATE00001"

    async def test_milestones_form_shows_scheme(
        self, schemes: SchemeRepository, async_client: AsyncFlaskClient
    ) -> None:
        scheme = build_scheme(
            reference="ATE00001", overview=build_scheme_overview(name="Wirral Package", authority_abbreviation="LIV")
        )
        scheme.financials.update_funding(build_scheme_funding())
        await schemes.add(scheme)

        change_milestone_dates_page = await ChangeMilestoneDatesPage.open(async_client, reference="ATE00001")

        assert change_milestone_dates_page.heading and change_milestone_dates_page.heading.caption == "Wirral Package"

    async def test_milestones_form_shows_fields(
        self, schemes: SchemeRepository, async_client: AsyncFlaskClient
    ) -> None:
        scheme = build_scheme(
            reference="ATE00001", overview=build_scheme_overview(name="Wirral Package", authority_abbreviation="LIV")
        )
        scheme.financials.update_funding(build_scheme_funding())
        await schemes.add(scheme)

        change_milestone_dates_page = await ChangeMilestoneDatesPage.open(async_client, reference="ATE00001")

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

    async def test_milestones_form_shows_milestone_heading(
        self, schemes: SchemeRepository, async_client: AsyncFlaskClient
    ) -> None:
        scheme = build_scheme(
            reference="ATE00001", overview=build_scheme_overview(name="Wirral Package", authority_abbreviation="LIV")
        )
        scheme.financials.update_funding(build_scheme_funding())
        await schemes.add(scheme)

        change_milestone_dates_page = await ChangeMilestoneDatesPage.open(async_client, reference="ATE00001")

        assert change_milestone_dates_page.form.detailed_design_completed_heading == "Detailed design completed"

    async def test_milestones_form_shows_date(self, schemes: SchemeRepository, async_client: AsyncFlaskClient) -> None:
        scheme = build_scheme(
            reference="ATE00001", overview=build_scheme_overview(name="Wirral Package", authority_abbreviation="LIV")
        )
        scheme.financials.update_funding(build_scheme_funding())
        scheme.milestones.update_milestones(
            SchemeMilestone(
                surrogate_id=1,
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 2),
                source=DataSource.ATF4_BID,
            )
        )
        await schemes.add(scheme)

        change_milestone_dates_page = await ChangeMilestoneDatesPage.open(async_client, reference="ATE00001")

        assert change_milestone_dates_page.form.detailed_design_completed_actual.value == "2 1 2020"

    async def test_milestones_form_shows_confirm(
        self, schemes: SchemeRepository, async_client: AsyncFlaskClient
    ) -> None:
        scheme = build_scheme(
            reference="ATE00001", overview=build_scheme_overview(name="Wirral Package", authority_abbreviation="LIV")
        )
        scheme.financials.update_funding(build_scheme_funding())
        await schemes.add(scheme)

        change_milestone_dates_page = await ChangeMilestoneDatesPage.open(async_client, reference="ATE00001")

        assert change_milestone_dates_page.form.confirm_url == "/schemes/ATE00001/milestones"

    async def test_milestones_form_shows_cancel(
        self, schemes: SchemeRepository, async_client: AsyncFlaskClient
    ) -> None:
        scheme = build_scheme(
            reference="ATE00001", overview=build_scheme_overview(name="Wirral Package", authority_abbreviation="LIV")
        )
        scheme.financials.update_funding(build_scheme_funding())
        await schemes.add(scheme)

        change_milestone_dates_page = await ChangeMilestoneDatesPage.open(async_client, reference="ATE00001")

        assert change_milestone_dates_page.form.cancel_url == "/schemes/ATE00001"

    async def test_cannot_milestones_form_when_different_authority(
        self, authorities: AuthorityRepository, schemes: SchemeRepository, async_client: AsyncFlaskClient
    ) -> None:
        await authorities.add(Authority(abbreviation="WYO", name="West Yorkshire Combined Authority"))
        scheme = build_scheme(
            reference="ATE00002",
            overview=build_scheme_overview(name="Hospital Fields Road", authority_abbreviation="WYO"),
        )
        scheme.financials.update_funding(build_scheme_funding())
        await schemes.add(scheme)

        forbidden_page = await ChangeMilestoneDatesPage.open_when_unauthorized(async_client, reference="ATE00002")

        assert forbidden_page.is_visible and forbidden_page.is_forbidden

    async def test_cannot_milestones_form_when_unknown_scheme(self, async_client: AsyncFlaskClient) -> None:
        not_found_page = await ChangeMilestoneDatesPage.open_when_not_found(async_client, reference="ATE00001")

        assert not_found_page.is_visible and not_found_page.is_not_found

    async def test_cannot_milestones_form_when_not_updateable_scheme(
        self, schemes: SchemeRepository, async_client: AsyncFlaskClient
    ) -> None:
        scheme = build_scheme(
            reference="ATE00001",
            overview=build_scheme_overview(name="Wirral Package", authority_abbreviation="LIV"),
            status=Status.PIPELINE,
        )
        scheme.financials.update_funding(build_scheme_funding())
        await schemes.add(scheme)

        not_found_page = await ChangeMilestoneDatesPage.open_when_not_found(async_client, reference="ATE00001")

        assert not_found_page.is_visible and not_found_page.is_not_found

    async def test_milestones_updates_milestones(
        self,
        clock: Clock,
        schemes: SchemeRepository,
        async_client: AsyncFlaskClient,
        csrf_token: str,
    ) -> None:
        clock.now = datetime(2020, 2, 1, 13)
        scheme = build_scheme(
            reference="ATE00001", overview=build_scheme_overview(name="Wirral Package", authority_abbreviation="LIV")
        )
        scheme.financials.update_funding(build_scheme_funding())
        scheme.milestones.update_milestones(
            SchemeMilestone(
                surrogate_id=1,
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 2),
                source=DataSource.ATF4_BID,
            )
        )
        await schemes.add(scheme)

        await async_client.post(
            "/schemes/ATE00001/milestones",
            data={"csrf_token": csrf_token, "detailed_design_completed-actual": ["3", "1", "2020"]},
        )

        actual_scheme = await schemes.get("ATE00001")
        assert actual_scheme
        (milestone,) = actual_scheme.milestones.milestones
        assert (
            milestone.surrogate_id is None
            and milestone.milestone == Milestone.DETAILED_DESIGN_COMPLETED
            and milestone.observation_type == ObservationType.ACTUAL
            and milestone.status_date == date(2020, 1, 3)
            and milestone.source == DataSource.AUTHORITY_UPDATE
        )

    async def test_milestones_shows_scheme(
        self, schemes: SchemeRepository, async_client: AsyncFlaskClient, csrf_token: str
    ) -> None:
        scheme = build_scheme(
            reference="ATE00001", overview=build_scheme_overview(name="Wirral Package", authority_abbreviation="LIV")
        )
        scheme.financials.update_funding(build_scheme_funding())
        await schemes.add(scheme)

        response = await async_client.post("/schemes/ATE00001/milestones", data={"csrf_token": csrf_token})

        assert response.status_code == 302 and response.location == "/schemes/ATE00001"

    async def test_cannot_milestones_when_error(
        self, schemes: SchemeRepository, async_client: AsyncFlaskClient, csrf_token: str
    ) -> None:
        scheme = build_scheme(
            reference="ATE00001", overview=build_scheme_overview(name="Wirral Package", authority_abbreviation="LIV")
        )
        scheme.financials.update_funding(build_scheme_funding())
        scheme.milestones.update_milestones(
            SchemeMilestone(
                surrogate_id=1,
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 2),
                source=DataSource.ATF4_BID,
            )
        )
        await schemes.add(scheme)

        change_milestone_dates_page = ChangeMilestoneDatesPage(
            await async_client.post(
                "/schemes/ATE00001/milestones",
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
        actual_scheme = await schemes.get("ATE00001")
        assert actual_scheme
        (milestone1,) = actual_scheme.milestones.milestones
        assert (
            milestone1.surrogate_id == 1
            and milestone1.milestone == Milestone.DETAILED_DESIGN_COMPLETED
            and milestone1.observation_type == ObservationType.ACTUAL
            and milestone1.status_date == date(2020, 1, 2)
            and milestone1.source == DataSource.ATF4_BID
        )

    async def test_cannot_milestones_when_future_actual_date(
        self, clock: Clock, schemes: SchemeRepository, async_client: AsyncFlaskClient, csrf_token: str
    ) -> None:
        clock.now = datetime(2020, 2, 1)
        scheme = build_scheme(
            reference="ATE00001", overview=build_scheme_overview(name="Wirral Package", authority_abbreviation="LIV")
        )
        scheme.financials.update_funding(build_scheme_funding())
        await schemes.add(scheme)

        change_milestone_dates_page = ChangeMilestoneDatesPage(
            await async_client.post(
                "/schemes/ATE00001/milestones",
                data=self.empty_change_milestone_dates_form()
                | {"csrf_token": csrf_token, "detailed_design_completed-actual": ["1", "3", "2020"]},
            )
        )

        assert change_milestone_dates_page.errors and list(change_milestone_dates_page.errors) == [
            "Detailed design completed actual date must not be in the future"
        ]

    async def test_cannot_milestones_when_no_csrf_token(
        self, schemes: SchemeRepository, async_client: AsyncFlaskClient
    ) -> None:
        scheme = build_scheme(
            reference="ATE00001", overview=build_scheme_overview(name="Wirral Package", authority_abbreviation="LIV")
        )
        scheme.financials.update_funding(build_scheme_funding())
        await schemes.add(scheme)

        change_milestone_dates_page = ChangeMilestoneDatesPage(
            await async_client.post("/schemes/ATE00001/milestones", follow_redirects=True)
        )

        assert change_milestone_dates_page.is_visible
        assert (
            change_milestone_dates_page.important_notification
            and change_milestone_dates_page.important_notification.heading
            == "The form you were submitting has expired. Please try again."
        )

    async def test_cannot_milestones_when_incorrect_csrf_token(
        self, schemes: SchemeRepository, async_client: AsyncFlaskClient, csrf_token: str
    ) -> None:
        scheme = build_scheme(
            reference="ATE00001", overview=build_scheme_overview(name="Wirral Package", authority_abbreviation="LIV")
        )
        scheme.financials.update_funding(build_scheme_funding())
        await schemes.add(scheme)

        change_milestone_dates_page = ChangeMilestoneDatesPage(
            await async_client.post("/schemes/ATE00001/milestones", data={"csrf_token": "x"}, follow_redirects=True)
        )

        assert change_milestone_dates_page.is_visible
        assert (
            change_milestone_dates_page.important_notification
            and change_milestone_dates_page.important_notification.heading
            == "The form you were submitting has expired. Please try again."
        )

    async def test_cannot_milestones_when_different_authority(
        self,
        authorities: AuthorityRepository,
        schemes: SchemeRepository,
        async_client: AsyncFlaskClient,
        csrf_token: str,
    ) -> None:
        await authorities.add(Authority(abbreviation="WYO", name="West Yorkshire Combined Authority"))
        scheme = build_scheme(
            reference="ATE00002",
            overview=build_scheme_overview(name="Hospital Fields Road", authority_abbreviation="WYO"),
        )
        scheme.financials.update_funding(build_scheme_funding())
        await schemes.add(scheme)

        response = await async_client.post("/schemes/ATE00002/milestones", data={"csrf_token": csrf_token})

        assert response.status_code == 403

    def test_cannot_milestones_when_unknown_scheme(self, client: FlaskClient, csrf_token: str) -> None:
        response = client.post("/schemes/ATE00001/milestones", data={"csrf_token": csrf_token})

        assert response.status_code == 404

    async def test_cannot_milestones_when_not_updateable_scheme(
        self, schemes: SchemeRepository, async_client: AsyncFlaskClient, csrf_token: str
    ) -> None:
        scheme = build_scheme(
            reference="ATE00001",
            overview=build_scheme_overview(name="Wirral Package", authority_abbreviation="LIV"),
            status=Status.PIPELINE,
        )
        scheme.financials.update_funding(build_scheme_funding())
        await schemes.add(scheme)

        response = await async_client.post("/schemes/ATE00001/milestones", data={"csrf_token": csrf_token})

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
