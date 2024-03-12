from datetime import date, datetime

import pytest
from flask.testing import FlaskClient

from schemes.domain.authorities import Authority, AuthorityRepository
from schemes.domain.dates import DateRange
from schemes.domain.schemes import (
    AuthorityReview,
    DataSource,
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


class TestSchemeOverview:
    @pytest.fixture(name="auth", autouse=True)
    def auth_fixture(self, authorities: AuthorityRepository, users: UserRepository, client: FlaskClient) -> None:
        authorities.add(Authority(id_=1, name="Liverpool City Region Combined Authority"))
        users.add(User(email="boardman@example.com", authority_id=1))
        with client.session_transaction() as session:
            session["user"] = {"email": "boardman@example.com"}

    def test_scheme_shows_minimal_overview(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        scheme_page = SchemePage.open(client, id_=1)

        assert (
            scheme_page.overview.reference == "ATE00001"
            and scheme_page.overview.scheme_type == ""
            and scheme_page.overview.funding_programme == ""
            and scheme_page.overview.current_milestone == ""
        )

    def test_scheme_shows_overview(self, schemes: SchemeRepository, client: FlaskClient) -> None:
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
        scheme.reviews.update_authority_review(
            AuthorityReview(id_=1, review_date=datetime(2020, 1, 2), source=DataSource.ATF4_BID)
        )
        schemes.add(scheme)

        scheme_page = SchemePage.open(client, id_=1)

        assert (
            scheme_page.overview.reference == "ATE00001"
            and scheme_page.overview.scheme_type == "Construction"
            and scheme_page.overview.funding_programme == "ATF4"
            and scheme_page.overview.current_milestone == "Detailed design completed"
        )
