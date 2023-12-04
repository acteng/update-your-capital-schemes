from datetime import date
from decimal import Decimal

import inject
import pytest
from flask import Flask
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
from tests.integration.pages import SchemePage


@pytest.fixture(name="users")
def users_fixture(app: Flask) -> UserRepository:
    return inject.instance(UserRepository)


@pytest.fixture(name="authorities")
def authorities_fixture(app: Flask) -> AuthorityRepository:
    return inject.instance(AuthorityRepository)


@pytest.fixture(name="schemes")
def schemes_fixture(app: Flask) -> SchemeRepository:
    return inject.instance(SchemeRepository)


@pytest.fixture(name="auth", autouse=True)
def auth_fixture(authorities: AuthorityRepository, users: UserRepository, client: FlaskClient) -> None:
    authorities.add(Authority(id_=1, name="Liverpool City Region Combined Authority"))
    users.add(User(email="boardman@example.com", authority_id=1))
    with client.session_transaction() as session:
        session["user"] = {"email": "boardman@example.com"}


def test_scheme_shows_back(schemes: SchemeRepository, client: FlaskClient) -> None:
    schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

    scheme_page = SchemePage(client).open(1)

    assert scheme_page.back_url == "/schemes"


def test_scheme_shows_name(schemes: SchemeRepository, client: FlaskClient) -> None:
    schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

    scheme_page = SchemePage(client).open(1)

    assert scheme_page.name == "Wirral Package"


def test_scheme_shows_minimal_overview(schemes: SchemeRepository, client: FlaskClient) -> None:
    schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

    scheme_page = SchemePage(client).open(1)

    assert (
        scheme_page.overview.reference == "ATE00001"
        and scheme_page.overview.scheme_type == "N/A"
        and scheme_page.overview.funding_programme == "N/A"
        and scheme_page.overview.current_milestone == "N/A"
    )


def test_scheme_shows_overview(schemes: SchemeRepository, client: FlaskClient) -> None:
    scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
    scheme.type = SchemeType.CONSTRUCTION
    scheme.funding_programme = FundingProgramme.ATF4
    scheme.milestones.update_milestone(
        MilestoneRevision(
            effective=DateRange(date(2020, 1, 1), None),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 1, 1),
        )
    )
    schemes.add(scheme)

    scheme_page = SchemePage(client).open(1)

    assert (
        scheme_page.overview.reference == "ATE00001"
        and scheme_page.overview.scheme_type == "Construction"
        and scheme_page.overview.funding_programme == "ATF4"
        and scheme_page.overview.current_milestone == "Detailed design completed"
    )


def test_scheme_shows_minimal_funding(schemes: SchemeRepository, client: FlaskClient) -> None:
    schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

    scheme_page = SchemePage(client).open(1)

    assert (
        scheme_page.funding.funding_allocation == "N/A"
        and scheme_page.funding.spend_to_date == "N/A"
        and scheme_page.funding.change_control_adjustment == "N/A"
        and scheme_page.funding.allocation_still_to_spend == "£0"
    )


def test_scheme_shows_funding(schemes: SchemeRepository, client: FlaskClient) -> None:
    scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
    scheme.funding.update_financials(
        FinancialRevision(
            effective=DateRange(date(2020, 1, 1), None),
            type=FinancialType.FUNDING_ALLOCATION,
            amount=Decimal(100000),
            source=DataSource.ATF4_BID,
        ),
        FinancialRevision(
            effective=DateRange(date(2020, 1, 1), None),
            type=FinancialType.SPENT_TO_DATE,
            amount=Decimal(50000),
            source=DataSource.ATF4_BID,
        ),
        FinancialRevision(
            effective=DateRange(date(2020, 1, 1), None),
            type=FinancialType.FUNDING_ALLOCATION,
            amount=Decimal(10000),
            source=DataSource.CHANGE_CONTROL,
        ),
    )
    schemes.add(scheme)

    scheme_page = SchemePage(client).open(1)

    assert (
        scheme_page.funding.funding_allocation == "£100,000"
        and scheme_page.funding.spend_to_date == "£50,000"
        and scheme_page.funding.change_control_adjustment == "£10,000"
        and scheme_page.funding.allocation_still_to_spend == "£60,000"
    )


def test_scheme_shows_zero_funding(schemes: SchemeRepository, client: FlaskClient) -> None:
    scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
    scheme.funding.update_financials(
        FinancialRevision(
            effective=DateRange(date(2020, 1, 1), None),
            type=FinancialType.FUNDING_ALLOCATION,
            amount=Decimal(0),
            source=DataSource.ATF4_BID,
        ),
        FinancialRevision(
            effective=DateRange(date(2020, 1, 1), None),
            type=FinancialType.SPENT_TO_DATE,
            amount=Decimal(0),
            source=DataSource.ATF4_BID,
        ),
        FinancialRevision(
            effective=DateRange(date(2020, 1, 1), None),
            type=FinancialType.FUNDING_ALLOCATION,
            amount=Decimal(0),
            source=DataSource.CHANGE_CONTROL,
        ),
    )
    schemes.add(scheme)

    scheme_page = SchemePage(client).open(1)

    assert (
        scheme_page.funding.funding_allocation == "£0"
        and scheme_page.funding.spend_to_date == "£0"
        and scheme_page.funding.change_control_adjustment == "£0"
        and scheme_page.funding.allocation_still_to_spend == "£0"
    )


def test_scheme_shows_minimal_milestones(schemes: SchemeRepository, client: FlaskClient) -> None:
    schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

    scheme_page = SchemePage(client).open(1)

    assert scheme_page.milestones.milestones.to_dicts() == [
        {"milestone": "Public consultation completed", "planned": "N/A", "actual": "N/A"},
        {"milestone": "Feasibility design completed", "planned": "N/A", "actual": "N/A"},
        {"milestone": "Preliminary design completed", "planned": "N/A", "actual": "N/A"},
        {"milestone": "Detailed design completed", "planned": "N/A", "actual": "N/A"},
        {"milestone": "Construction started", "planned": "N/A", "actual": "N/A"},
        {"milestone": "Construction completed", "planned": "N/A", "actual": "N/A"},
    ]


def test_scheme_shows_milestones(schemes: SchemeRepository, client: FlaskClient) -> None:
    scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
    current = DateRange(date(2020, 1, 1), None)
    scheme.milestones.update_milestones(
        MilestoneRevision(current, Milestone.PUBLIC_CONSULTATION_COMPLETED, ObservationType.PLANNED, date(2020, 1, 1)),
        MilestoneRevision(current, Milestone.PUBLIC_CONSULTATION_COMPLETED, ObservationType.ACTUAL, date(2020, 1, 2)),
        MilestoneRevision(current, Milestone.FEASIBILITY_DESIGN_COMPLETED, ObservationType.PLANNED, date(2020, 2, 1)),
        MilestoneRevision(current, Milestone.FEASIBILITY_DESIGN_COMPLETED, ObservationType.ACTUAL, date(2020, 2, 2)),
        MilestoneRevision(current, Milestone.PRELIMINARY_DESIGN_COMPLETED, ObservationType.PLANNED, date(2020, 3, 1)),
        MilestoneRevision(current, Milestone.PRELIMINARY_DESIGN_COMPLETED, ObservationType.ACTUAL, date(2020, 3, 2)),
        MilestoneRevision(current, Milestone.DETAILED_DESIGN_COMPLETED, ObservationType.PLANNED, date(2020, 4, 1)),
        MilestoneRevision(current, Milestone.DETAILED_DESIGN_COMPLETED, ObservationType.ACTUAL, date(2020, 4, 2)),
        MilestoneRevision(current, Milestone.CONSTRUCTION_STARTED, ObservationType.PLANNED, date(2020, 5, 1)),
        MilestoneRevision(current, Milestone.CONSTRUCTION_STARTED, ObservationType.ACTUAL, date(2020, 5, 2)),
        MilestoneRevision(current, Milestone.CONSTRUCTION_COMPLETED, ObservationType.PLANNED, date(2020, 6, 1)),
        MilestoneRevision(current, Milestone.CONSTRUCTION_COMPLETED, ObservationType.ACTUAL, date(2020, 6, 2)),
    )
    schemes.add(scheme)

    scheme_page = SchemePage(client).open(1)

    assert scheme_page.milestones.milestones.to_dicts() == [
        {"milestone": "Public consultation completed", "planned": "01/01/2020", "actual": "02/01/2020"},
        {"milestone": "Feasibility design completed", "planned": "01/02/2020", "actual": "02/02/2020"},
        {"milestone": "Preliminary design completed", "planned": "01/03/2020", "actual": "02/03/2020"},
        {"milestone": "Detailed design completed", "planned": "01/04/2020", "actual": "02/04/2020"},
        {"milestone": "Construction started", "planned": "01/05/2020", "actual": "02/05/2020"},
        {"milestone": "Construction completed", "planned": "01/06/2020", "actual": "02/06/2020"},
    ]


def test_scheme_shows_minimal_outputs(schemes: SchemeRepository, client: FlaskClient) -> None:
    scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
    scheme.outputs.update_outputs(
        OutputRevision(
            effective=DateRange(date(2020, 1, 1), None),
            type_measure=OutputTypeMeasure.NEW_SEGREGATED_CYCLING_FACILITY_NUMBER_OF_JUNCTIONS,
            value=Decimal(1),
            observation_type=ObservationType.ACTUAL,
        ),
        OutputRevision(
            effective=DateRange(date(2020, 1, 1), None),
            type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
            value=Decimal(2),
            observation_type=ObservationType.PLANNED,
        ),
    )
    schemes.add(scheme)

    scheme_page = SchemePage(client).open(1)

    outputs = list(scheme_page.outputs.outputs)
    assert outputs[0].planned == "N/A" and outputs[1].actual == "N/A"


def test_scheme_shows_outputs(schemes: SchemeRepository, client: FlaskClient) -> None:
    scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
    scheme.outputs.update_outputs(
        OutputRevision(
            effective=DateRange(date(2020, 1, 1), None),
            type_measure=OutputTypeMeasure.NEW_SEGREGATED_CYCLING_FACILITY_MILES,
            value=Decimal("3.000000"),
            observation_type=ObservationType.PLANNED,
        ),
        OutputRevision(
            effective=DateRange(date(2020, 1, 1), None),
            type_measure=OutputTypeMeasure.NEW_SEGREGATED_CYCLING_FACILITY_MILES,
            value=Decimal("4.000000"),
            observation_type=ObservationType.ACTUAL,
        ),
        OutputRevision(
            effective=DateRange(date(2020, 1, 1), None),
            type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_NUMBER_OF_JUNCTIONS,
            value=Decimal("2.600000"),
            observation_type=ObservationType.PLANNED,
        ),
        OutputRevision(
            effective=DateRange(date(2020, 1, 1), None),
            type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_NUMBER_OF_JUNCTIONS,
            value=Decimal("2.700000"),
            observation_type=ObservationType.ACTUAL,
        ),
    )
    schemes.add(scheme)

    scheme_page = SchemePage(client).open(1)

    assert scheme_page.outputs.outputs.to_dicts() == [
        {
            "infrastructure": "New segregated cycling facility",
            "measurement": "miles",
            "planned": "3",
            "actual": "4",
        },
        {
            "infrastructure": "Improvements to make an existing walking/cycle route safer",
            "measurement": "number of junctions",
            "planned": "2.6",
            "actual": "2.7",
        },
    ]


@pytest.mark.parametrize(
    "value, expected_value", [(Decimal("0.000000"), "0"), (Decimal("0.100000"), "0.1"), (Decimal("10.000000"), "10")]
)
def test_scheme_shows_formatted_outputs(
    schemes: SchemeRepository, client: FlaskClient, value: Decimal, expected_value: str
) -> None:
    scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
    scheme.outputs.update_outputs(
        OutputRevision(
            effective=(DateRange(date(2020, 1, 1), None)),
            type_measure=OutputTypeMeasure.NEW_SEGREGATED_CYCLING_FACILITY_NUMBER_OF_JUNCTIONS,
            value=value,
            observation_type=ObservationType.PLANNED,
        ),
        OutputRevision(
            effective=(DateRange(date(2020, 1, 1), None)),
            type_measure=OutputTypeMeasure.NEW_SEGREGATED_CYCLING_FACILITY_NUMBER_OF_JUNCTIONS,
            value=value,
            observation_type=ObservationType.ACTUAL,
        ),
    )
    schemes.add(scheme)

    scheme_page = SchemePage(client).open(1)

    outputs = list(scheme_page.outputs.outputs)
    assert outputs[0].planned == expected_value and outputs[0].actual == expected_value
