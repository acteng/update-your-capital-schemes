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
    scheme.update_milestone(
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
    scheme.update_financials(
        FinancialRevision(
            effective=DateRange(date(2020, 1, 1), None),
            type=FinancialType.FUNDING_ALLOCATION,
            amount=Decimal("100000"),
            source=DataSource.ATF4_BID,
        ),
        FinancialRevision(
            effective=DateRange(date(2020, 1, 1), None),
            type=FinancialType.SPENT_TO_DATE,
            amount=Decimal("50000"),
            source=DataSource.ATF4_BID,
        ),
        FinancialRevision(
            effective=DateRange(date(2020, 1, 1), None),
            type=FinancialType.FUNDING_ALLOCATION,
            amount=Decimal("10000"),
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
    scheme.update_financials(
        FinancialRevision(
            effective=DateRange(date(2020, 1, 1), None),
            type=FinancialType.FUNDING_ALLOCATION,
            amount=Decimal("0"),
            source=DataSource.ATF4_BID,
        ),
        FinancialRevision(
            effective=DateRange(date(2020, 1, 1), None),
            type=FinancialType.SPENT_TO_DATE,
            amount=Decimal("0"),
            source=DataSource.ATF4_BID,
        ),
        FinancialRevision(
            effective=DateRange(date(2020, 1, 1), None),
            type=FinancialType.FUNDING_ALLOCATION,
            amount=Decimal("0"),
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
