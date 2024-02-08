from datetime import date, datetime
from decimal import Decimal
from typing import Any, Mapping

import pytest
from flask.testing import FlaskClient

from schemes.domain.authorities import Authority, AuthorityRepository
from schemes.domain.schemes import (
    DataSource,
    DateRange,
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
from tests.integration.pages import (
    ChangeMilestoneDatesPage,
    ChangeSpendToDatePage,
    SchemePage,
)


@pytest.fixture(name="auth", autouse=True)
def auth_fixture(authorities: AuthorityRepository, users: UserRepository, client: FlaskClient) -> None:
    authorities.add(Authority(id_=1, name="Liverpool City Region Combined Authority"))
    users.add(User(email="boardman@example.com", authority_id=1))
    with client.session_transaction() as session:
        session["user"] = {"email": "boardman@example.com"}


def test_scheme_shows_html(schemes: SchemeRepository, client: FlaskClient) -> None:
    schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))
    chromium_default_accept = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"

    response = client.get("/schemes/1", headers={"Accept": chromium_default_accept})

    assert response.status_code == 200 and response.content_type == "text/html; charset=utf-8"


def test_scheme_shows_back(schemes: SchemeRepository, client: FlaskClient) -> None:
    schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

    scheme_page = SchemePage.open(client, id_=1)

    assert scheme_page.back_url == "/schemes"


def test_scheme_shows_authority(schemes: SchemeRepository, client: FlaskClient) -> None:
    schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

    scheme_page = SchemePage.open(client, id_=1)

    assert scheme_page.authority == "Liverpool City Region Combined Authority"


def test_scheme_shows_name(schemes: SchemeRepository, client: FlaskClient) -> None:
    schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

    scheme_page = SchemePage.open(client, id_=1)

    assert scheme_page.name == "Wirral Package"


def test_scheme_shows_minimal_overview(schemes: SchemeRepository, client: FlaskClient) -> None:
    schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

    scheme_page = SchemePage.open(client, id_=1)

    assert (
        scheme_page.overview.reference == "ATE00001"
        and scheme_page.overview.scheme_type == ""
        and scheme_page.overview.funding_programme == ""
        and scheme_page.overview.current_milestone == ""
    )


def test_scheme_shows_overview(schemes: SchemeRepository, client: FlaskClient) -> None:
    scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
    scheme.type = SchemeType.CONSTRUCTION
    scheme.funding_programme = FundingProgramme.ATF4
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
    )


def test_scheme_shows_minimal_funding(schemes: SchemeRepository, client: FlaskClient) -> None:
    schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

    scheme_page = SchemePage.open(client, id_=1)

    assert (
        scheme_page.funding.funding_allocation == ""
        and scheme_page.funding.change_control_adjustment == ""
        and scheme_page.funding.spend_to_date == ""
        and scheme_page.funding.allocation_still_to_spend == "£0"
    )


def test_scheme_shows_funding(schemes: SchemeRepository, client: FlaskClient) -> None:
    scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
    scheme.funding.update_financials(
        FinancialRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1), None),
            type_=FinancialType.FUNDING_ALLOCATION,
            amount=100_000,
            source=DataSource.ATF4_BID,
        ),
        FinancialRevision(
            id_=2,
            effective=DateRange(datetime(2020, 1, 1), None),
            type_=FinancialType.FUNDING_ALLOCATION,
            amount=10_000,
            source=DataSource.CHANGE_CONTROL,
        ),
        FinancialRevision(
            id_=3,
            effective=DateRange(datetime(2020, 1, 1), None),
            type_=FinancialType.SPENT_TO_DATE,
            amount=50_000,
            source=DataSource.ATF4_BID,
        ),
    )
    schemes.add(scheme)

    scheme_page = SchemePage.open(client, id_=1)

    assert (
        scheme_page.funding.funding_allocation == "£100,000"
        and scheme_page.funding.change_control_adjustment == "£10,000"
        and scheme_page.funding.spend_to_date == "£50,000"
        and scheme_page.funding.allocation_still_to_spend == "£60,000"
    )


def test_scheme_shows_zero_funding(schemes: SchemeRepository, client: FlaskClient) -> None:
    scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
    scheme.funding.update_financials(
        FinancialRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1), None),
            type_=FinancialType.FUNDING_ALLOCATION,
            amount=0,
            source=DataSource.ATF4_BID,
        ),
        FinancialRevision(
            id_=2,
            effective=DateRange(datetime(2020, 1, 1), None),
            type_=FinancialType.SPENT_TO_DATE,
            amount=0,
            source=DataSource.ATF4_BID,
        ),
        FinancialRevision(
            id_=3,
            effective=DateRange(datetime(2020, 1, 1), None),
            type_=FinancialType.FUNDING_ALLOCATION,
            amount=0,
            source=DataSource.CHANGE_CONTROL,
        ),
    )
    schemes.add(scheme)

    scheme_page = SchemePage.open(client, id_=1)

    assert (
        scheme_page.funding.funding_allocation == "£0"
        and scheme_page.funding.change_control_adjustment == "£0"
        and scheme_page.funding.spend_to_date == "£0"
        and scheme_page.funding.allocation_still_to_spend == "£0"
    )


def test_scheme_shows_change_spend_to_date(schemes: SchemeRepository, client: FlaskClient) -> None:
    schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

    scheme_page = SchemePage.open(client, id_=1)

    assert scheme_page.funding.change_spend_to_date_url == "/schemes/1/spend-to-date"


def test_scheme_shows_change_milestones(schemes: SchemeRepository, client: FlaskClient) -> None:
    schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

    scheme_page = SchemePage.open(client, id_=1)

    assert scheme_page.milestones.change_milestones_url == "/schemes/1/milestones"


def test_scheme_shows_minimal_milestones(schemes: SchemeRepository, client: FlaskClient) -> None:
    schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

    scheme_page = SchemePage.open(client, id_=1)

    assert scheme_page.milestones.milestones.to_dicts() == [
        {"milestone": "Feasibility design completed", "planned": "", "actual": ""},
        {"milestone": "Preliminary design completed", "planned": "", "actual": ""},
        {"milestone": "Detailed design completed", "planned": "", "actual": ""},
        {"milestone": "Construction started", "planned": "", "actual": ""},
        {"milestone": "Construction completed", "planned": "", "actual": ""},
    ]


def test_scheme_shows_milestones(schemes: SchemeRepository, client: FlaskClient) -> None:
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
            7, current, Milestone.CONSTRUCTION_STARTED, ObservationType.PLANNED, date(2020, 5, 1), DataSource.ATF4_BID
        ),
        MilestoneRevision(
            8, current, Milestone.CONSTRUCTION_STARTED, ObservationType.ACTUAL, date(2020, 5, 2), DataSource.ATF4_BID
        ),
        MilestoneRevision(
            9, current, Milestone.CONSTRUCTION_COMPLETED, ObservationType.PLANNED, date(2020, 6, 1), DataSource.ATF4_BID
        ),
        MilestoneRevision(
            10, current, Milestone.CONSTRUCTION_COMPLETED, ObservationType.ACTUAL, date(2020, 6, 2), DataSource.ATF4_BID
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


def test_scheme_shows_minimal_outputs(schemes: SchemeRepository, client: FlaskClient) -> None:
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


def test_scheme_shows_outputs(schemes: SchemeRepository, client: FlaskClient) -> None:
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


def test_scheme_shows_zero_outputs(schemes: SchemeRepository, client: FlaskClient) -> None:
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


def test_scheme_shows_message_when_no_outputs(schemes: SchemeRepository, client: FlaskClient) -> None:
    schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

    scheme_page = SchemePage.open(client, id_=1)

    assert not scheme_page.outputs.outputs
    assert scheme_page.outputs.is_no_outputs_message_visible


def test_cannot_scheme_when_different_authority(
    authorities: AuthorityRepository, schemes: SchemeRepository, client: FlaskClient
) -> None:
    authorities.add(Authority(id_=2, name="West Yorkshire Combined Authority"))
    schemes.add(Scheme(id_=2, name="Hospital Fields Road", authority_id=2))

    forbidden_page = SchemePage.open_when_unauthorized(client, id_=2)

    assert forbidden_page.is_visible and forbidden_page.is_forbidden


def test_spend_to_date_form_shows_back(schemes: SchemeRepository, client: FlaskClient) -> None:
    schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

    change_spend_to_date_page = ChangeSpendToDatePage.open(client, id_=1)

    assert change_spend_to_date_page.back_url == "/schemes/1"


def test_spend_to_date_form_shows_funding_summary(schemes: SchemeRepository, client: FlaskClient) -> None:
    scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
    scheme.funding.update_financials(
        FinancialRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1), None),
            type_=FinancialType.FUNDING_ALLOCATION,
            amount=100_000,
            source=DataSource.ATF4_BID,
        ),
        FinancialRevision(
            id_=2,
            effective=DateRange(datetime(2020, 1, 1), None),
            type_=FinancialType.FUNDING_ALLOCATION,
            amount=10_000,
            source=DataSource.CHANGE_CONTROL,
        ),
    )
    schemes.add(scheme)

    change_spend_to_date_page = ChangeSpendToDatePage.open(client, id_=1)

    assert (
        change_spend_to_date_page.funding_summary
        == "This scheme has £100,000 of funding allocation and £10,000 of change control adjustment."
    )


def test_spend_to_date_form_shows_minimal_funding_summary(schemes: SchemeRepository, client: FlaskClient) -> None:
    schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

    change_spend_to_date_page = ChangeSpendToDatePage.open(client, id_=1)

    assert (
        change_spend_to_date_page.funding_summary
        == "This scheme has no funding allocation and no change control adjustment."
    )


def test_spend_to_date_form_shows_amount(schemes: SchemeRepository, client: FlaskClient) -> None:
    scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
    scheme.funding.update_financial(
        FinancialRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1, 12), None),
            type_=FinancialType.SPENT_TO_DATE,
            amount=50_000,
            source=DataSource.ATF4_BID,
        )
    )
    schemes.add(scheme)

    change_spend_to_date_page = ChangeSpendToDatePage.open(client, id_=1)

    assert change_spend_to_date_page.title == "Schemes - Active Travel England - GOV.UK"
    assert change_spend_to_date_page.form.amount.value == "50000"


def test_spend_to_date_form_shows_zero_amount(schemes: SchemeRepository, client: FlaskClient) -> None:
    scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
    scheme.funding.update_financial(
        FinancialRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1, 12), None),
            type_=FinancialType.SPENT_TO_DATE,
            amount=0,
            source=DataSource.ATF4_BID,
        )
    )
    schemes.add(scheme)

    change_spend_to_date_page = ChangeSpendToDatePage.open(client, id_=1)

    assert change_spend_to_date_page.form.amount.value == "0"


def test_spend_to_date_form_shows_empty_amount(schemes: SchemeRepository, client: FlaskClient) -> None:
    schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

    change_spend_to_date_page = ChangeSpendToDatePage.open(client, id_=1)

    assert not change_spend_to_date_page.form.amount.value


def test_spend_to_date_form_shows_confirm(schemes: SchemeRepository, client: FlaskClient) -> None:
    schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

    change_spend_to_date_page = ChangeSpendToDatePage.open(client, id_=1)

    assert change_spend_to_date_page.form.confirm_url == "/schemes/1/spend-to-date"


def test_spend_to_date_form_shows_cancel(schemes: SchemeRepository, client: FlaskClient) -> None:
    schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

    change_spend_to_date_page = ChangeSpendToDatePage.open(client, id_=1)

    assert change_spend_to_date_page.form.cancel_url == "/schemes/1"


def test_cannot_spend_to_date_form_when_different_authority(
    authorities: AuthorityRepository, schemes: SchemeRepository, client: FlaskClient
) -> None:
    authorities.add(Authority(id_=2, name="West Yorkshire Combined Authority"))
    schemes.add(Scheme(id_=2, name="Hospital Fields Road", authority_id=2))

    forbidden_page = ChangeSpendToDatePage.open_when_unauthorized(client, id_=2)

    assert forbidden_page.is_visible and forbidden_page.is_forbidden


def test_spend_to_date_updates_spend_to_date(
    clock: Clock, schemes: SchemeRepository, client: FlaskClient, csrf_token: str
) -> None:
    clock.now = datetime(2020, 1, 31, 13)
    scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
    scheme.funding.update_financials(
        FinancialRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1, 12), None),
            type_=FinancialType.FUNDING_ALLOCATION,
            amount=100_000,
            source=DataSource.ATF4_BID,
        ),
        FinancialRevision(
            id_=2,
            effective=DateRange(datetime(2020, 1, 1, 12), None),
            type_=FinancialType.SPENT_TO_DATE,
            amount=50_000,
            source=DataSource.ATF4_BID,
        ),
    )
    schemes.add(scheme)

    client.post("/schemes/1/spend-to-date", data={"csrf_token": csrf_token, "amount": "60000"})

    actual_scheme = schemes.get(1)
    assert actual_scheme
    financial_revision1: FinancialRevision
    financial_revision2: FinancialRevision
    financial_revision3: FinancialRevision
    financial_revision1, financial_revision2, financial_revision3 = actual_scheme.funding.financial_revisions
    assert financial_revision2.id == 2 and financial_revision2.effective.date_to == datetime(2020, 1, 31, 13)
    assert (
        financial_revision3.effective == DateRange(datetime(2020, 1, 31, 13), None)
        and financial_revision3.type == FinancialType.SPENT_TO_DATE
        and financial_revision3.amount == 60_000
        and financial_revision3.source == DataSource.AUTHORITY_UPDATE
    )


def test_spend_to_date_shows_scheme(schemes: SchemeRepository, client: FlaskClient, csrf_token: str) -> None:
    scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
    scheme.funding.update_financial(
        FinancialRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1, 12), None),
            type_=FinancialType.FUNDING_ALLOCATION,
            amount=100_000,
            source=DataSource.ATF4_BID,
        )
    )
    schemes.add(scheme)

    response = client.post("/schemes/1/spend-to-date", data={"csrf_token": csrf_token, "amount": "60000"})

    assert response.status_code == 302 and response.location == "/schemes/1"


def test_cannot_spend_to_date_when_error(schemes: SchemeRepository, client: FlaskClient, csrf_token: str) -> None:
    scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
    scheme.funding.update_financial(
        FinancialRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1, 12), None),
            type_=FinancialType.SPENT_TO_DATE,
            amount=50_000,
            source=DataSource.ATF4_BID,
        )
    )
    schemes.add(scheme)

    change_spend_to_date_page = ChangeSpendToDatePage(
        client.post("/schemes/1/spend-to-date", data={"csrf_token": csrf_token, "amount": ""})
    )

    assert change_spend_to_date_page.title == "Error: Schemes - Active Travel England - GOV.UK"
    assert change_spend_to_date_page.errors and list(change_spend_to_date_page.errors) == ["Enter spend to date"]
    assert (
        change_spend_to_date_page.form.amount.is_errored
        and change_spend_to_date_page.form.amount.error == "Error: Enter spend to date"
        and change_spend_to_date_page.form.amount.value is None
    )
    actual_scheme = schemes.get(1)
    assert actual_scheme
    financial_revision1: FinancialRevision
    (financial_revision1,) = actual_scheme.funding.financial_revisions
    assert (
        financial_revision1.id == 1
        and financial_revision1.effective == DateRange(datetime(2020, 1, 1, 12), None)
        and financial_revision1.type == FinancialType.SPENT_TO_DATE
        and financial_revision1.amount == 50_000
        and financial_revision1.source == DataSource.ATF4_BID
    )


def test_cannot_spend_to_date_when_no_csrf_token(schemes: SchemeRepository, client: FlaskClient) -> None:
    schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

    change_spend_to_date_page = ChangeSpendToDatePage(
        client.post("/schemes/1/spend-to-date", data={"amount": "60000"}, follow_redirects=True)
    )

    assert change_spend_to_date_page.is_visible
    assert (
        change_spend_to_date_page.notification_banner
        and change_spend_to_date_page.notification_banner.heading
        == "The form you were submitting has expired. Please try again."
    )


def test_cannot_spend_to_date_when_incorrect_csrf_token(
    schemes: SchemeRepository, client: FlaskClient, csrf_token: str
) -> None:
    schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

    change_spend_to_date_page = ChangeSpendToDatePage(
        client.post("/schemes/1/spend-to-date", data={"csrf_token": "x", "amount": "60000"}, follow_redirects=True)
    )

    assert change_spend_to_date_page.is_visible
    assert (
        change_spend_to_date_page.notification_banner
        and change_spend_to_date_page.notification_banner.heading
        == "The form you were submitting has expired. Please try again."
    )


def test_cannot_spend_to_date_when_different_authority(
    authorities: AuthorityRepository, schemes: SchemeRepository, client: FlaskClient, csrf_token: str
) -> None:
    authorities.add(Authority(id_=2, name="West Yorkshire Combined Authority"))
    schemes.add(Scheme(id_=2, name="Hospital Fields Road", authority_id=2))

    response = client.post("/schemes/2/spend-to-date", data={"csrf_token": csrf_token, "amount": "60000"})

    assert response.status_code == 403


def test_milestones_form_shows_back(schemes: SchemeRepository, client: FlaskClient) -> None:
    schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

    change_milestone_dates_page = ChangeMilestoneDatesPage.open(client, id_=1)

    assert change_milestone_dates_page.back_url == "/schemes/1"


@pytest.mark.parametrize(
    "observation_type, observation_type_item",
    [(ObservationType.PLANNED, "planned"), (ObservationType.ACTUAL, "actual")],
)
def test_milestones_form_shows_date(
    schemes: SchemeRepository, client: FlaskClient, observation_type: ObservationType, observation_type_item: str
) -> None:
    scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
    scheme.milestones.update_milestones(
        MilestoneRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1, 12), None),
            milestone=Milestone.CONSTRUCTION_STARTED,
            observation_type=observation_type,
            status_date=date(2020, 1, 2),
            source=DataSource.ATF4_BID,
        )
    )
    schemes.add(scheme)

    change_milestone_dates_page = ChangeMilestoneDatesPage.open(client, id_=1)

    assert change_milestone_dates_page.title == "Schemes - Active Travel England - GOV.UK"
    # TODO: remove leading zeros, see: https://github.com/LandRegistry/govuk-frontend-wtf/issues/85
    # assert change_milestone_dates_page.form.construction_started[observation_type_item].value == "2 1 2020"
    assert change_milestone_dates_page.form.construction_started[observation_type_item].value == "02 01 2020"


def test_milestones_form_shows_confirm(schemes: SchemeRepository, client: FlaskClient) -> None:
    schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

    change_milestone_dates_page = ChangeMilestoneDatesPage.open(client, id_=1)

    assert change_milestone_dates_page.form.confirm_url == "/schemes/1/milestones"


def test_milestones_form_shows_cancel(schemes: SchemeRepository, client: FlaskClient) -> None:
    schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

    change_milestone_dates_page = ChangeMilestoneDatesPage.open(client, id_=1)

    assert change_milestone_dates_page.form.cancel_url == "/schemes/1"


def test_cannot_milestones_form_when_different_authority(
    authorities: AuthorityRepository, schemes: SchemeRepository, client: FlaskClient
) -> None:
    authorities.add(Authority(id_=2, name="West Yorkshire Combined Authority"))
    schemes.add(Scheme(id_=2, name="Hospital Fields Road", authority_id=2))

    forbidden_page = ChangeMilestoneDatesPage.open_when_unauthorized(client, id_=2)

    assert forbidden_page.is_visible and forbidden_page.is_forbidden


@pytest.mark.parametrize(
    "observation_type, field_name", [(ObservationType.PLANNED, "planned"), (ObservationType.ACTUAL, "actual")]
)
def test_milestones_updates_milestones(
    clock: Clock,
    schemes: SchemeRepository,
    client: FlaskClient,
    csrf_token: str,
    observation_type: ObservationType,
    field_name: str,
) -> None:
    clock.now = datetime(2020, 1, 31, 13)
    scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
    scheme.milestones.update_milestones(
        MilestoneRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1, 12), None),
            milestone=Milestone.CONSTRUCTION_STARTED,
            observation_type=observation_type,
            status_date=date(2020, 1, 2),
            source=DataSource.ATF4_BID,
        )
    )
    schemes.add(scheme)

    client.post("/schemes/1/milestones", data={"csrf_token": csrf_token, field_name: ["3", "1", "2020"]})

    actual_scheme = schemes.get(1)
    assert actual_scheme
    milestone_revision1: MilestoneRevision
    milestone_revision2: MilestoneRevision
    milestone_revision1, milestone_revision2 = actual_scheme.milestones.milestone_revisions
    assert milestone_revision1.id == 1 and milestone_revision1.effective.date_to == datetime(2020, 1, 31, 13)
    assert (
        milestone_revision2.effective == DateRange(datetime(2020, 1, 31, 13), None)
        and milestone_revision2.milestone == Milestone.CONSTRUCTION_STARTED
        and milestone_revision2.observation_type == observation_type
        and milestone_revision2.status_date == date(2020, 1, 3)
        and milestone_revision2.source == DataSource.AUTHORITY_UPDATE
    )


def test_milestones_shows_scheme(schemes: SchemeRepository, client: FlaskClient, csrf_token: str) -> None:
    schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

    response = client.post(
        "/schemes/1/milestones", data={"csrf_token": csrf_token, "planned": ["3", "1", "2020"], "actual": ["", "", ""]}
    )

    assert response.status_code == 302 and response.location == "/schemes/1"


@pytest.mark.parametrize(
    "observation_type, field_name, observation_type_item, expected_error",
    [
        (ObservationType.PLANNED, "planned", "planned", "Construction started planned date must be a real date"),
        (ObservationType.ACTUAL, "actual", "actual", "Construction started actual date must be a real date"),
    ],
)
def test_cannot_milestones_when_error(
    schemes: SchemeRepository,
    client: FlaskClient,
    csrf_token: str,
    observation_type: ObservationType,
    field_name: str,
    observation_type_item: str,
    expected_error: str,
) -> None:
    scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
    scheme.milestones.update_milestones(
        MilestoneRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1, 12), None),
            milestone=Milestone.CONSTRUCTION_STARTED,
            observation_type=observation_type,
            status_date=date(2020, 1, 2),
            source=DataSource.ATF4_BID,
        )
    )
    schemes.add(scheme)
    empty_data = {"csrf_token": csrf_token, "planned": ["", "", ""], "actual": ["", "", ""]}

    change_milestone_dates_page = ChangeMilestoneDatesPage(
        client.post("/schemes/1/milestones", data=empty_data | {field_name: ["x", "x", "x"]})
    )

    assert change_milestone_dates_page.title == "Error: Schemes - Active Travel England - GOV.UK"
    assert change_milestone_dates_page.errors and list(change_milestone_dates_page.errors) == [expected_error]
    assert (
        change_milestone_dates_page.form.construction_started[observation_type_item].is_errored
        and change_milestone_dates_page.form.construction_started[observation_type_item].error
        == f"Error: {expected_error}"
        and change_milestone_dates_page.form.construction_started[observation_type_item].value == "x x x"
    )
    actual_scheme = schemes.get(1)
    assert actual_scheme
    milestone_revision1: MilestoneRevision
    (milestone_revision1,) = actual_scheme.milestones.milestone_revisions
    assert (
        milestone_revision1.id == 1
        and milestone_revision1.effective == DateRange(datetime(2020, 1, 1, 12), None)
        and milestone_revision1.milestone == Milestone.CONSTRUCTION_STARTED
        and milestone_revision1.observation_type == observation_type
        and milestone_revision1.status_date == date(2020, 1, 2)
        and milestone_revision1.source == DataSource.ATF4_BID
    )


def test_cannot_milestones_when_no_csrf_token(schemes: SchemeRepository, client: FlaskClient) -> None:
    schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

    change_milestone_dates_page = ChangeMilestoneDatesPage(
        client.post(
            "/schemes/1/milestones", data={"planned": ["3", "1", "2020"], "actual": ["", "", ""]}, follow_redirects=True
        )
    )

    assert change_milestone_dates_page.is_visible
    assert (
        change_milestone_dates_page.notification_banner
        and change_milestone_dates_page.notification_banner.heading
        == "The form you were submitting has expired. Please try again."
    )


def test_cannot_milestones_when_incorrect_csrf_token(
    schemes: SchemeRepository, client: FlaskClient, csrf_token: str
) -> None:
    schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

    change_milestone_dates_page = ChangeMilestoneDatesPage(
        client.post(
            "/schemes/1/milestones",
            data={"csrf_token": "x", "planned": ["3", "1", "2020"], "actual": ["", "", ""]},
            follow_redirects=True,
        )
    )

    assert change_milestone_dates_page.is_visible
    assert (
        change_milestone_dates_page.notification_banner
        and change_milestone_dates_page.notification_banner.heading
        == "The form you were submitting has expired. Please try again."
    )


def test_cannot_milestones_when_different_authority(
    authorities: AuthorityRepository, schemes: SchemeRepository, client: FlaskClient, csrf_token: str
) -> None:
    authorities.add(Authority(id_=2, name="West Yorkshire Combined Authority"))
    schemes.add(Scheme(id_=2, name="Hospital Fields Road", authority_id=2))

    response = client.post(
        "/schemes/2/milestones", data={"csrf_token": csrf_token, "planned": ["3", "1", "2020"], "actual": ["", "", ""]}
    )

    assert response.status_code == 403


class TestApiEnabled:
    @pytest.fixture(name="config")
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
            "financial_revisions": [],
            "milestone_revisions": [],
            "output_revisions": [],
        }

    def test_cannot_get_scheme_when_no_credentials(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        response = client.get("/schemes/1", headers={"Accept": "application/json"})

        assert response.status_code == 401

    def test_cannot_get_scheme_when_incorrect_credentials(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        response = client.get("/schemes/1", headers={"Accept": "application/json", "Authorization": "API-Key obree"})

        assert response.status_code == 401


class TestApiDisabled:
    def test_cannot_get_scheme(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        response = client.get("/schemes/1", headers={"Accept": "application/json", "Authorization": "API-Key boardman"})

        assert response.status_code == 401
