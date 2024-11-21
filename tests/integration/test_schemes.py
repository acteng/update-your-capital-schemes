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
    SchemeRepository,
    SchemeType,
)
from schemes.domain.users import User, UserRepository
from schemes.infrastructure.clock import Clock
from tests.builders import build_scheme
from tests.integration.pages import SchemesPage


class TestSchemes:
    @pytest.fixture(name="auth", autouse=True)
    def auth_fixture(self, authorities: AuthorityRepository, users: UserRepository, client: FlaskClient) -> None:
        authorities.add(Authority(id_=1, name="Liverpool City Region Combined Authority"))
        users.add(User(email="boardman@example.com", authority_id=1))
        with client.session_transaction() as session:
            session["user"] = {"email": "boardman@example.com"}

    def test_schemes_shows_title(self, client: FlaskClient) -> None:
        schemes_page = SchemesPage.open(client)

        assert schemes_page.title == "Your schemes - Update your capital schemes - Active Travel England - GOV.UK"

    @pytest.mark.parametrize(
        "now, expected_notification_banner",
        [
            (datetime(2020, 4, 24, 12), "You have 7 days left to update your schemes"),
            (datetime(2020, 4, 30, 12), "You have 1 day left to update your schemes"),
            (datetime(2020, 5, 1, 12), "Your scheme updates are overdue"),
        ],
    )
    def test_schemes_shows_update_schemes_notification(
        self,
        client: FlaskClient,
        clock: Clock,
        now: datetime,
        schemes: SchemeRepository,
        expected_notification_banner: str,
    ) -> None:
        clock.now = now
        scheme = build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_id=1)
        scheme.reviews.update_authority_review(
            AuthorityReview(id_=1, review_date=datetime(2020, 1, 2), source=DataSource.ATF3_BID)
        )
        schemes.add(scheme)

        schemes_page = SchemesPage.open(client)

        assert (
            schemes_page.important_notification
            and schemes_page.important_notification.heading == expected_notification_banner
        )

    def test_schemes_does_not_show_notification_when_up_to_date(
        self, client: FlaskClient, clock: Clock, schemes: SchemeRepository
    ) -> None:
        clock.now = datetime(2020, 3, 1)
        scheme = build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_id=1)
        scheme.reviews.update_authority_review(
            AuthorityReview(id_=1, review_date=datetime(2020, 1, 2), source=DataSource.ATF3_BID)
        )
        schemes.add(scheme)

        schemes_page = SchemesPage.open(client)

        assert not schemes_page.important_notification

    def test_schemes_shows_authority(self, client: FlaskClient) -> None:
        schemes_page = SchemesPage.open(client)

        assert schemes_page.heading and schemes_page.heading.caption == "Liverpool City Region Combined Authority"

    def test_schemes_shows_schemes(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(
            build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_id=1),
            build_scheme(id_=2, reference="ATE00002", name="School Streets", authority_id=1),
            build_scheme(
                id_=3, reference="ATE00003", name="Runcorn Busway", authority_id=1, bid_status=BidStatus.SUBMITTED
            ),
            build_scheme(id_=4, reference="ATE00004", name="Hospital Fields Road", authority_id=2),
            build_scheme(id_=5, reference="ATE00005", overview_revisions=[]),
        )

        schemes_page = SchemesPage.open(client)

        assert schemes_page.schemes
        assert [row.reference for row in schemes_page.schemes] == ["ATE00001", "ATE00002"]
        assert not schemes_page.is_no_schemes_message_visible

    def test_schemes_shows_minimal_scheme(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(
            build_scheme(
                id_=1,
                reference="ATE00001",
                name="Wirral Package",
                authority_id=1,
                funding_programme=FundingProgrammes.ATF3,
            )
        )

        schemes_page = SchemesPage.open(client)

        assert schemes_page.schemes
        assert schemes_page.schemes.to_dicts() == [
            {
                "reference": "ATE00001",
                "funding_programme": "ATF3",
                "name": "Wirral Package",
                "needs_review": True,
                "last_reviewed": "",
            }
        ]

    def test_schemes_shows_scheme(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        scheme = build_scheme(
            id_=1, reference="ATE00001", name="Wirral Package", authority_id=1, funding_programme=FundingProgrammes.ATF3
        )
        scheme.reviews.update_authority_review(
            AuthorityReview(id_=1, review_date=datetime(2020, 1, 2, 12), source=DataSource.ATF3_BID)
        )
        schemes.add(scheme)

        schemes_page = SchemesPage.open(client)

        assert schemes_page.schemes
        assert schemes_page.schemes.to_dicts() == [
            {
                "reference": "ATE00001",
                "funding_programme": "ATF3",
                "name": "Wirral Package",
                "needs_review": False,
                "last_reviewed": "2 Jan 2020",
            }
        ]

    def test_schemes_shows_scheme_needs_review(
        self, clock: Clock, schemes: SchemeRepository, client: FlaskClient
    ) -> None:
        clock.now = datetime(2023, 4, 24)
        scheme = build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_id=1)
        scheme.reviews.update_authority_review(
            AuthorityReview(id_=1, review_date=datetime(2023, 1, 2), source=DataSource.ATF3_BID)
        )
        schemes.add(scheme)

        schemes_page = SchemesPage.open(client)

        assert schemes_page.schemes
        assert [row.needs_review for row in schemes_page.schemes] == [True]

    def test_scheme_shows_scheme(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_id=1))

        schemes_page = SchemesPage.open(client)

        assert schemes_page.schemes
        assert schemes_page.schemes["ATE00001"].reference_url == "/schemes/1"

    def test_schemes_shows_message_when_no_schemes(self, client: FlaskClient) -> None:
        schemes_page = SchemesPage.open(client)

        assert not schemes_page.schemes
        assert schemes_page.is_no_schemes_message_visible


class TestSchemesApi:
    @pytest.fixture(name="config", scope="class")
    def config_fixture(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        return dict(config) | {"API_KEY": "boardman"}

    def test_add_schemes(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        response = client.post(
            "/schemes",
            headers={"Authorization": "API-Key boardman"},
            json=[{"id": 1, "reference": "ATE00001"}, {"id": 2, "reference": "ATE00002"}],
        )

        assert response.status_code == 201
        scheme1 = schemes.get(1)
        scheme2 = schemes.get(2)
        assert scheme1 and scheme1.id == 1 and scheme1.reference == "ATE00001"
        assert scheme2 and scheme2.id == 2 and scheme2.reference == "ATE00002"

    def test_add_schemes_overview_revisions(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        response = client.post(
            "/schemes",
            headers={"Authorization": "API-Key boardman"},
            json=[
                {
                    "id": 1,
                    "reference": "ATE00001",
                    "overview_revisions": [
                        {
                            "id": 2,
                            "effective_date_from": "2020-01-01T12:00:00",
                            "effective_date_to": None,
                            "name": "Wirral Package",
                            "authority_id": 1,
                            "type": "construction",
                            "funding_programme": "ATF4",
                        }
                    ],
                },
            ],
        )

        assert response.status_code == 201
        scheme1 = schemes.get(1)
        assert scheme1 and scheme1.id == 1
        overview_revision1: OverviewRevision
        (overview_revision1,) = scheme1.overview.overview_revisions
        assert (
            overview_revision1.id == 2
            and overview_revision1.effective == DateRange(datetime(2020, 1, 1, 12), None)
            and overview_revision1.name == "Wirral Package"
            and overview_revision1.authority_id == 1
            and overview_revision1.type == SchemeType.CONSTRUCTION
            and overview_revision1.funding_programme == FundingProgrammes.ATF4
        )

    def test_add_schemes_bid_status_revisions(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        response = client.post(
            "/schemes",
            headers={"Authorization": "API-Key boardman"},
            json=[
                {
                    "id": 1,
                    "reference": "ATE00001",
                    "bid_status_revisions": [
                        {
                            "id": 2,
                            "effective_date_from": "2020-01-01T12:00:00",
                            "effective_date_to": None,
                            "status": "funded",
                        }
                    ],
                },
            ],
        )

        assert response.status_code == 201
        scheme1 = schemes.get(1)
        assert scheme1 and scheme1.id == 1
        bid_status_revision1: BidStatusRevision
        (bid_status_revision1,) = scheme1.funding.bid_status_revisions
        assert (
            bid_status_revision1.id == 2
            and bid_status_revision1.effective == DateRange(datetime(2020, 1, 1, 12), None)
            and bid_status_revision1.status == BidStatus.FUNDED
        )

    def test_add_schemes_financial_revisions(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        response = client.post(
            "/schemes",
            headers={"Authorization": "API-Key boardman"},
            json=[
                {
                    "id": 1,
                    "reference": "ATE00001",
                    "financial_revisions": [
                        {
                            "id": 2,
                            "effective_date_from": "2020-01-01T12:00:00",
                            "effective_date_to": None,
                            "type": "funding allocation",
                            "amount": 100_000,
                            "source": "ATF4 bid",
                        }
                    ],
                },
            ],
        )

        assert response.status_code == 201
        scheme1 = schemes.get(1)
        assert scheme1 and scheme1.id == 1
        financial_revision1: FinancialRevision
        (financial_revision1,) = scheme1.funding.financial_revisions
        assert (
            financial_revision1.id == 2
            and financial_revision1.effective == DateRange(datetime(2020, 1, 1, 12), None)
            and financial_revision1.type == FinancialType.FUNDING_ALLOCATION
            and financial_revision1.amount == 100_000
            and financial_revision1.source == DataSource.ATF4_BID
        )

    def test_add_schemes_milestone_revisions(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        response = client.post(
            "/schemes",
            headers={"Authorization": "API-Key boardman"},
            json=[
                {
                    "id": 1,
                    "reference": "ATE00001",
                    "milestone_revisions": [
                        {
                            "id": 2,
                            "effective_date_from": "2020-01-01T12:00:00",
                            "effective_date_to": None,
                            "milestone": "detailed design completed",
                            "observation_type": "actual",
                            "status_date": "2020-01-01",
                            "source": "ATF4 bid",
                        }
                    ],
                },
            ],
        )

        assert response.status_code == 201
        scheme1 = schemes.get(1)
        assert scheme1 and scheme1.id == 1
        milestone_revision1: MilestoneRevision
        (milestone_revision1,) = scheme1.milestones.milestone_revisions
        assert (
            milestone_revision1.id == 2
            and milestone_revision1.effective == DateRange(datetime(2020, 1, 1, 12), None)
            and milestone_revision1.milestone == Milestone.DETAILED_DESIGN_COMPLETED
            and milestone_revision1.observation_type == ObservationType.ACTUAL
            and milestone_revision1.status_date == date(2020, 1, 1)
            and milestone_revision1.source == DataSource.ATF4_BID
        )

    def test_add_schemes_output_revisions(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        response = client.post(
            "/schemes",
            headers={"Authorization": "API-Key boardman"},
            json=[
                {
                    "id": 1,
                    "reference": "ATE00001",
                    "output_revisions": [
                        {
                            "id": 2,
                            "effective_date_from": "2020-01-01T12:00:00",
                            "effective_date_to": None,
                            "type": "improvements to make an existing walking/cycle route safer",
                            "measure": "miles",
                            "value": "10",
                            "observation_type": "actual",
                        }
                    ],
                },
            ],
        )

        assert response.status_code == 201
        scheme1 = schemes.get(1)
        assert scheme1 and scheme1.id == 1
        output_revision1: OutputRevision
        (output_revision1,) = scheme1.outputs.output_revisions
        assert (
            output_revision1.id == 2
            and output_revision1.effective == DateRange(datetime(2020, 1, 1, 12), None)
            and output_revision1.type_measure == OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES
            and output_revision1.value == Decimal(10)
            and output_revision1.observation_type == ObservationType.ACTUAL
        )

    def test_add_schemes_authority_reviews(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        response = client.post(
            "/schemes",
            headers={"Authorization": "API-Key boardman"},
            json=[
                {
                    "id": 1,
                    "reference": "ATE00001",
                    "authority_reviews": [
                        {
                            "id": 2,
                            "review_date": "2020-01-01T12:00:00",
                            "source": "ATF4 bid",
                        }
                    ],
                },
            ],
        )

        assert response.status_code == 201
        scheme1 = schemes.get(1)
        assert scheme1 and scheme1.id == 1
        authority_review1: AuthorityReview
        (authority_review1,) = scheme1.reviews.authority_reviews
        assert (
            authority_review1.id == 2
            and authority_review1.review_date == datetime(2020, 1, 1, 12)
            and authority_review1.source == DataSource.ATF4_BID
        )

    def test_cannot_add_schemes_when_no_credentials(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        response = client.post("/schemes", json=[{"id": 1, "reference": "ATE00001"}])

        assert response.status_code == 401
        assert not schemes.get(1)

    def test_cannot_add_schemes_when_incorrect_credentials(
        self, schemes: SchemeRepository, client: FlaskClient
    ) -> None:
        response = client.post(
            "/schemes", headers={"Authorization": "API-Key obree"}, json=[{"id": 1, "reference": "ATE00001"}]
        )

        assert response.status_code == 401
        assert not schemes.get(1)

    def test_cannot_add_schemes_with_invalid_repr(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        response = client.post(
            "/schemes",
            headers={"Authorization": "API-Key boardman"},
            json=[{"id": 1, "reference": "ATE00001", "foo": "bar"}],
        )

        assert response.status_code == 400
        assert not schemes.get(1)

    def test_clear_schemes(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_id=1))

        response = client.delete("/schemes", headers={"Authorization": "API-Key boardman"})

        assert response.status_code == 204
        assert not schemes.get(1)

    def test_cannot_clear_schemes_when_no_credentials(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_id=1))

        response = client.delete("/schemes")

        assert response.status_code == 401
        assert schemes.get(1)

    def test_cannot_clear_schemes_when_incorrect_credentials(
        self, schemes: SchemeRepository, client: FlaskClient
    ) -> None:
        schemes.add(build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_id=1))

        response = client.delete("/schemes", headers={"Authorization": "API-Key obree"})

        assert response.status_code == 401
        assert schemes.get(1)


class TestSchemesApiWhenDisabled:
    def test_cannot_add_schemes(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        response = client.post(
            "/schemes", headers={"Authorization": "API-Key boardman"}, json=[{"id": 1, "reference": "ATE00001"}]
        )

        assert response.status_code == 401
        assert not schemes.get(1)

    def test_cannot_clear_schemes(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_id=1))

        response = client.delete("/schemes", headers={"Authorization": "API-Key boardman"})

        assert response.status_code == 401
        assert schemes.get(1)
