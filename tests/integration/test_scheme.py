from datetime import date, datetime
from decimal import Decimal
from typing import Any, Mapping

import pytest
from flask.testing import FlaskClient

from schemes.domain.authorities import Authority, AuthorityRepository
from schemes.domain.dates import DateRange
from schemes.domain.schemes import (
    AuthorityReview,
    BidStatus,
    BidStatusRevision,
    DataSource,
    FinancialRevision,
    FinancialType,
    FundingProgrammes,
    Milestone,
    MilestoneRevision,
    ObservationType,
    OutputRevision,
    OutputTypeMeasure,
    OverviewRevision,
    Scheme,
    SchemeRepository,
    SchemeType,
)
from schemes.domain.users import User, UserRepository
from schemes.infrastructure.clock import Clock
from tests.builders import build_scheme
from tests.integration.pages import SchemePage


class TestScheme:
    @pytest.fixture(name="auth", autouse=True)
    def auth_fixture(self, authorities: AuthorityRepository, users: UserRepository, client: FlaskClient) -> None:
        authorities.add(Authority(id_=1, name="Liverpool City Region Combined Authority"))
        users.add(User(email="boardman@example.com", authority_id=1))
        with client.session_transaction() as session:
            session["user"] = {"email": "boardman@example.com"}

    def test_scheme_shows_html(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(build_scheme(id_=1, name="Wirral Package", authority_id=1))
        chromium_default_accept = (
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
        )

        response = client.get("/schemes/1", headers={"Accept": chromium_default_accept})

        assert response.status_code == 200 and response.content_type == "text/html; charset=utf-8"

    def test_scheme_shows_back(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(build_scheme(id_=1, name="Wirral Package", authority_id=1))

        scheme_page = SchemePage.open(client, id_=1)

        assert scheme_page.back_url == "/schemes"

    def test_scheme_shows_authority(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(build_scheme(id_=1, name="Wirral Package", authority_id=1))

        scheme_page = SchemePage.open(client, id_=1)

        assert scheme_page.authority == "Liverpool City Region Combined Authority"

    def test_scheme_shows_name(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(build_scheme(id_=1, name="Wirral Package", authority_id=1))

        scheme_page = SchemePage.open(client, id_=1)

        assert scheme_page.name == "Wirral Package"

    @pytest.mark.parametrize(
        "review_date, expected_needs_review",
        [
            pytest.param(datetime(2023, 1, 2), True, id="review before reporting window"),
            pytest.param(datetime(2023, 4, 1), False, id="review during reporting window"),
        ],
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
        scheme = build_scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme.reviews.update_authority_review(
            AuthorityReview(id_=1, review_date=review_date, source=DataSource.ATF4_BID)
        )
        schemes.add(scheme)

        scheme_page = SchemePage.open(client, id_=1)

        assert scheme_page.needs_review == expected_needs_review

    def test_cannot_scheme_when_different_authority(
        self, authorities: AuthorityRepository, schemes: SchemeRepository, client: FlaskClient
    ) -> None:
        authorities.add(Authority(id_=2, name="West Yorkshire Combined Authority"))
        schemes.add(build_scheme(id_=2, name="Hospital Fields Road", authority_id=2))

        forbidden_page = SchemePage.open_when_unauthorized(client, id_=2)

        assert forbidden_page.is_visible and forbidden_page.is_forbidden

    def test_cannot_scheme_when_no_authority(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(build_scheme(id_=2, overview_revisions=[]))

        forbidden_page = SchemePage.open_when_unauthorized(client, id_=2)

        assert forbidden_page.is_visible and forbidden_page.is_forbidden

    def test_cannot_scheme_when_unknown_scheme(self, client: FlaskClient) -> None:
        not_found_page = SchemePage.open_when_not_found(client, id_=1)

        assert not_found_page.is_visible and not_found_page.is_not_found

    def test_cannot_scheme_when_not_updateable_scheme(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(build_scheme(id_=1, name="Wirral Package", authority_id=1, bid_status=BidStatus.SUBMITTED))

        not_found_page = SchemePage.open_when_not_found(client, id_=1)

        assert not_found_page.is_visible and not_found_page.is_not_found


class TestSchemeApi:
    @pytest.fixture(name="config", scope="class")
    def config_fixture(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        return dict(config) | {"API_KEY": "boardman"}

    def test_get_scheme(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(Scheme(id_=1, funding_programme=FundingProgrammes.ATF4))

        response = client.get("/schemes/1", headers={"Accept": "application/json", "Authorization": "API-Key boardman"})

        assert response.json == {
            "id": 1,
            "funding_programme": "ATF4",
            "overview_revisions": [],
            "bid_status_revisions": [],
            "financial_revisions": [],
            "milestone_revisions": [],
            "output_revisions": [],
            "authority_reviews": [],
        }

    def test_get_scheme_overview_revisions(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        scheme = build_scheme(
            id_=1,
            overview_revisions=[
                OverviewRevision(
                    id_=2,
                    effective=DateRange(datetime(2020, 1, 1, 12), None),
                    name="Wirral Package",
                    authority_id=1,
                    type_=SchemeType.CONSTRUCTION,
                )
            ],
        )
        schemes.add(scheme)

        response = client.get("/schemes/1", headers={"Accept": "application/json", "Authorization": "API-Key boardman"})

        assert response.json and response.json["id"] == 1
        assert response.json["overview_revisions"] == [
            {
                "id": 2,
                "effective_date_from": "2020-01-01T12:00:00",
                "effective_date_to": None,
                "name": "Wirral Package",
                "authority_id": 1,
                "type": "construction",
            }
        ]

    def test_get_scheme_bid_status_revisions(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        scheme = build_scheme(
            id_=1,
            name="Wirral Package",
            authority_id=1,
            bid_status_revisions=[
                BidStatusRevision(id_=2, effective=DateRange(datetime(2020, 1, 1, 12), None), status=BidStatus.FUNDED)
            ],
        )
        schemes.add(scheme)

        response = client.get("/schemes/1", headers={"Accept": "application/json", "Authorization": "API-Key boardman"})

        assert response.json and response.json["id"] == 1
        assert response.json["bid_status_revisions"] == [
            {
                "id": 2,
                "effective_date_from": "2020-01-01T12:00:00",
                "effective_date_to": None,
                "status": "funded",
            }
        ]

    def test_get_scheme_financial_revisions(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        scheme = build_scheme(id_=1, name="Wirral Package", authority_id=1)
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
        scheme = build_scheme(id_=1, name="Wirral Package", authority_id=1)
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
        scheme = build_scheme(id_=1, name="Wirral Package", authority_id=1)
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

    def test_get_scheme_authority_reviews(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        scheme = build_scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme.reviews.update_authority_review(
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

    def test_cannot_get_scheme_when_no_credentials(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(build_scheme(id_=1, name="Wirral Package", authority_id=1))

        response = client.get("/schemes/1", headers={"Accept": "application/json"})

        assert response.status_code == 401

    def test_cannot_get_scheme_when_incorrect_credentials(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(build_scheme(id_=1, name="Wirral Package", authority_id=1))

        response = client.get("/schemes/1", headers={"Accept": "application/json", "Authorization": "API-Key obree"})

        assert response.status_code == 401


class TestSchemeApiWhenDisabled:
    def test_cannot_get_scheme(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(build_scheme(id_=1, name="Wirral Package", authority_id=1))

        response = client.get("/schemes/1", headers={"Accept": "application/json", "Authorization": "API-Key boardman"})

        assert response.status_code == 401
