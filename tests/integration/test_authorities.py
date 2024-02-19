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
    SchemeRepository,
    SchemeType,
)
from schemes.domain.users import UserRepository


class TestApiEnabled:
    @pytest.fixture(name="config")
    def config_fixture(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        return dict(config) | {"API_KEY": "boardman"}

    def test_add_authorities(self, authorities: AuthorityRepository, client: FlaskClient) -> None:
        response = client.post(
            "/authorities",
            headers={"Authorization": "API-Key boardman"},
            json=[
                {"id": 1, "name": "Liverpool City Region Combined Authority"},
                {"id": 2, "name": "West Yorkshire Combined Authority"},
            ],
        )

        assert response.status_code == 201
        authority1 = authorities.get(1)
        authority2 = authorities.get(2)
        assert authority1 and authority1.id == 1 and authority1.name == "Liverpool City Region Combined Authority"
        assert authority2 and authority2.id == 2 and authority2.name == "West Yorkshire Combined Authority"

    def test_cannot_add_authorities_when_no_credentials(
        self, authorities: AuthorityRepository, client: FlaskClient
    ) -> None:
        response = client.post("/authorities", json=[{"id": 1, "name": "Liverpool City Region Combined Authority"}])

        assert response.status_code == 401
        assert not authorities.get(1)

    def test_cannot_add_authorities_when_incorrect_credentials(
        self, authorities: AuthorityRepository, client: FlaskClient
    ) -> None:
        response = client.post(
            "/authorities",
            headers={"Authorization": "API-Key obree"},
            json=[{"id": 1, "name": "Liverpool City Region Combined Authority"}],
        )

        assert response.status_code == 401
        assert not authorities.get(1)

    def test_cannot_add_authorities_with_invalid_repr(
        self, authorities: AuthorityRepository, client: FlaskClient
    ) -> None:
        response = client.post(
            "/authorities",
            headers={"Authorization": "API-Key boardman"},
            json=[{"id": 1, "name": "Liverpool City Region Combined Authority", "foo": "bar"}],
        )

        assert response.status_code == 400
        assert not authorities.get(1)

    def test_add_users(self, users: UserRepository, client: FlaskClient) -> None:
        response = client.post(
            "/authorities/1/users",
            headers={"Authorization": "API-Key boardman"},
            json=[{"email": "boardman@example.com"}, {"email": "obree@example.com"}],
        )

        assert response.status_code == 201
        user1 = users.get_by_email("boardman@example.com")
        user2 = users.get_by_email("obree@example.com")
        assert user1 and user1.email == "boardman@example.com" and user1.authority_id == 1
        assert user2 and user2.email == "obree@example.com" and user2.authority_id == 1

    def test_cannot_add_users_when_no_credentials(self, users: UserRepository, client: FlaskClient) -> None:
        response = client.post("/authorities/1/users", json=[{"email": "boardman@example.com"}])

        assert response.status_code == 401
        assert not users.get_by_email("boardman@example.com")

    def test_cannot_add_users_when_incorrect_credentials(self, users: UserRepository, client: FlaskClient) -> None:
        response = client.post(
            "/authorities/1/users", headers={"Authorization": "API-Key obree"}, json=[{"email": "boardman@example.com"}]
        )

        assert response.status_code == 401
        assert not users.get_by_email("boardman@example.com")

    def test_cannot_add_users_with_invalid_repr(self, users: UserRepository, client: FlaskClient) -> None:
        response = client.post(
            "/authorities/1/users",
            headers={"Authorization": "API-Key boardman"},
            json=[{"email": "boardman@example.com", "foo": "bar"}],
        )

        assert response.status_code == 400
        assert not users.get_by_email("boardman@example.com")

    def test_add_schemes(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        response = client.post(
            "/authorities/1/schemes",
            headers={"Authorization": "API-Key boardman"},
            json=[
                {"id": 1, "name": "Wirral Package", "type": "construction", "funding_programme": "ATF4"},
                {"id": 2, "name": "School Streets"},
            ],
        )

        assert response.status_code == 201
        scheme1 = schemes.get(1)
        scheme2 = schemes.get(2)
        assert (
            scheme1
            and scheme1.id == 1
            and scheme1.name == "Wirral Package"
            and scheme1.authority_id == 1
            and scheme1.type == SchemeType.CONSTRUCTION
            and scheme1.funding_programme == FundingProgramme.ATF4
        )
        assert scheme2 and scheme2.id == 2 and scheme2.name == "School Streets" and scheme2.authority_id == 1

    def test_add_schemes_financial_revisions(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        response = client.post(
            "/authorities/1/schemes",
            headers={"Authorization": "API-Key boardman"},
            json=[
                {
                    "id": 1,
                    "name": "Wirral Package",
                    "financial_revisions": [
                        {
                            "id": 2,
                            "effective_date_from": "2020-01-01T12:00:00",
                            "effective_date_to": None,
                            "type": "funding allocation",
                            "amount": 100_000,
                            "source": "ATF4 Bid",
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
            "/authorities/1/schemes",
            headers={"Authorization": "API-Key boardman"},
            json=[
                {
                    "id": 1,
                    "name": "Wirral Package",
                    "milestone_revisions": [
                        {
                            "id": 2,
                            "effective_date_from": "2020-01-01T12:00:00",
                            "effective_date_to": None,
                            "milestone": "detailed design completed",
                            "observation_type": "Actual",
                            "status_date": "2020-01-01",
                            "source": "ATF4 Bid",
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
            "/authorities/1/schemes",
            headers={"Authorization": "API-Key boardman"},
            json=[
                {
                    "id": 1,
                    "name": "Wirral Package",
                    "output_revisions": [
                        {
                            "id": 2,
                            "effective_date_from": "2020-01-01T12:00:00",
                            "effective_date_to": None,
                            "type": "Improvements to make an existing walking/cycle route safer",
                            "measure": "miles",
                            "value": "10",
                            "observation_type": "Actual",
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

    def test_cannot_add_schemes_when_no_credentials(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        response = client.post("/authorities/1/schemes", json=[{"id": 1, "name": "Wirral Package"}])

        assert response.status_code == 401
        assert not schemes.get(1)

    def test_cannot_add_schemes_when_incorrect_credentials(
        self, schemes: SchemeRepository, client: FlaskClient
    ) -> None:
        response = client.post(
            "/authorities/1/schemes",
            headers={"Authorization": "API-Key obree"},
            json=[{"id": 1, "name": "Wirral Package"}],
        )

        assert response.status_code == 401
        assert not schemes.get(1)

    def test_cannot_add_schemes_with_invalid_repr(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        response = client.post(
            "/authorities/1/schemes",
            headers={"Authorization": "API-Key boardman"},
            json=[{"id": 1, "name": "Wirral Package", "foo": "bar"}],
        )

        assert response.status_code == 400
        assert not schemes.get(1)

    def test_clear_authorities(self, authorities: AuthorityRepository, client: FlaskClient) -> None:
        authorities.add(Authority(id_=1, name="Liverpool City Region Combined Authority"))

        response = client.delete("/authorities", headers={"Authorization": "API-Key boardman"})

        assert response.status_code == 204
        assert not authorities.get(1)

    def test_cannot_clear_authorities_when_no_credentials(
        self, authorities: AuthorityRepository, client: FlaskClient
    ) -> None:
        authorities.add(Authority(id_=1, name="Liverpool City Region Combined Authority"))

        response = client.delete("/authorities")

        assert response.status_code == 401
        assert authorities.get(1)

    def test_cannot_clear_authorities_when_incorrect_credentials(
        self, authorities: AuthorityRepository, client: FlaskClient
    ) -> None:
        authorities.add(Authority(id_=1, name="Liverpool City Region Combined Authority"))

        response = client.delete("/authorities", headers={"Authorization": "API-Key obree"})

        assert response.status_code == 401
        assert authorities.get(1)


class TestApiDisabled:
    def test_cannot_add_authorities(self, authorities: AuthorityRepository, client: FlaskClient) -> None:
        response = client.post(
            "/authorities",
            headers={"Authorization": "API-Key boardman"},
            json=[{"id": 1, "name": "Liverpool City Region Combined Authority"}],
        )

        assert response.status_code == 401
        assert not authorities.get(1)

    def test_cannot_add_users(self, users: UserRepository, client: FlaskClient) -> None:
        response = client.post(
            "/authorities/1/users",
            headers={"Authorization": "API-Key boardman"},
            json=[{"email": "boardman@example.com"}],
        )

        assert response.status_code == 401
        assert not users.get_by_email("boardman@example.com")

    def test_cannot_add_schemes(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        response = client.post(
            "/authorities/1/schemes",
            headers={"Authorization": "API-Key boardman"},
            json=[{"id": 1, "name": "Wirral Package"}],
        )

        assert response.status_code == 401
        assert not schemes.get(1)

    def test_cannot_clear_authorities(self, authorities: AuthorityRepository, client: FlaskClient) -> None:
        authorities.add(Authority(id_=1, name="Liverpool City Region Combined Authority"))

        response = client.delete("/authorities", headers={"Authorization": "API-Key boardman"})

        assert response.status_code == 401
        assert authorities.get(1)
