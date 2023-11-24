from datetime import date
from decimal import Decimal
from typing import Any, Mapping

import inject
import pytest
from flask import Flask
from flask.testing import FlaskClient

from schemes.domain.authorities import Authority
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
    SchemeType,
)
from schemes.domain.users import User
from schemes.services.authorities import AuthorityRepository
from schemes.services.schemes import SchemeRepository
from schemes.services.users import UserRepository


@pytest.fixture(name="authorities")
def authorities_fixture(app: Flask) -> AuthorityRepository:
    return inject.instance(AuthorityRepository)


@pytest.fixture(name="users")
def users_fixture(app: Flask) -> UserRepository:
    return inject.instance(UserRepository)


@pytest.fixture(name="schemes")
def schemes_fixture(app: Flask) -> SchemeRepository:
    return inject.instance(SchemeRepository)


class TestApiEnabled:
    @pytest.fixture(name="config")
    def config_fixture(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        return config | {"API_KEY": "boardman"}

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
        authority1: Authority
        authority2: Authority
        (authority1, authority2) = authorities.get_all()
        assert authority1.id == 1 and authority1.name == "Liverpool City Region Combined Authority"
        assert authority2.id == 2 and authority2.name == "West Yorkshire Combined Authority"

    def test_cannot_add_authorities_when_no_credentials(
        self, authorities: AuthorityRepository, client: FlaskClient
    ) -> None:
        response = client.post("/authorities", json=[{"id": 1, "name": "Liverpool City Region Combined Authority"}])

        assert response.status_code == 401
        assert not authorities.get_all()

    def test_cannot_add_authorities_when_incorrect_credentials(
        self, authorities: AuthorityRepository, client: FlaskClient
    ) -> None:
        response = client.post(
            "/authorities",
            headers={"Authorization": "API-Key obree"},
            json=[{"id": 1, "name": "Liverpool City Region Combined Authority"}],
        )

        assert response.status_code == 401
        assert not authorities.get_all()

    def test_add_users(self, users: UserRepository, client: FlaskClient) -> None:
        response = client.post(
            "/authorities/1/users",
            headers={"Authorization": "API-Key boardman"},
            json=[{"email": "boardman@example.com"}, {"email": "obree@example.com"}],
        )

        assert response.status_code == 201
        user1: User
        user2: User
        (user1, user2) = users.get_all()
        assert user1.email == "boardman@example.com" and user2.authority_id == 1
        assert user2.email == "obree@example.com" and user2.authority_id == 1

    def test_cannot_add_users_when_no_credentials(self, users: UserRepository, client: FlaskClient) -> None:
        response = client.post("/authorities/1/users", json=[{"email": "boardman@example.com"}])

        assert response.status_code == 401
        assert not users.get_all()

    def test_cannot_add_users_when_incorrect_credentials(self, users: UserRepository, client: FlaskClient) -> None:
        response = client.post(
            "/authorities/1/users", headers={"Authorization": "API-Key obree"}, json=[{"email": "boardman@example.com"}]
        )

        assert response.status_code == 401
        assert not users.get_all()

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
        scheme1: Scheme
        scheme2: Scheme
        scheme1, scheme2 = schemes.get_all()
        assert (
            scheme1.id == 1
            and scheme1.name == "Wirral Package"
            and scheme1.authority_id == 1
            and scheme1.type == SchemeType.CONSTRUCTION
            and scheme1.funding_programme == FundingProgramme.ATF4
        )
        assert scheme2.id == 2 and scheme2.name == "School Streets" and scheme2.authority_id == 1

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
                            "effective_date_from": "2020-01-01",
                            "effective_date_to": None,
                            "milestone": "detailed design completed",
                            "observation_type": "Actual",
                            "status_date": "2020-01-01",
                        }
                    ],
                },
            ],
        )

        assert response.status_code == 201
        scheme1: Scheme
        (scheme1,) = schemes.get_all()
        assert scheme1.id == 1
        assert scheme1.milestone_revisions == [
            MilestoneRevision(
                effective=DateRange(date(2020, 1, 1), None),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 1),
            )
        ]

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
                            "effective_date_from": "2020-01-01",
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
        scheme1: Scheme
        (scheme1,) = schemes.get_all()
        assert scheme1.id == 1
        assert scheme1.financial_revisions == [
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal("100000"),
                source=DataSource.ATF4_BID,
            )
        ]

    def test_clear_authorities(self, authorities: AuthorityRepository, client: FlaskClient) -> None:
        authorities.add(Authority(id_=1, name="Liverpool City Region Combined Authority"))

        response = client.delete("/authorities", headers={"Authorization": "API-Key boardman"})

        assert response.status_code == 204
        assert not authorities.get_all()

    def test_cannot_clear_authorities_when_no_credentials(
        self, authorities: AuthorityRepository, client: FlaskClient
    ) -> None:
        authorities.add(Authority(id_=1, name="Liverpool City Region Combined Authority"))

        response = client.delete("/authorities")

        assert response.status_code == 401
        assert [authority.id for authority in authorities.get_all()] == [1]

    def test_cannot_clear_authorities_when_incorrect_credentials(
        self, authorities: AuthorityRepository, client: FlaskClient
    ) -> None:
        authorities.add(Authority(id_=1, name="Liverpool City Region Combined Authority"))

        response = client.delete("/authorities", headers={"Authorization": "API-Key obree"})

        assert response.status_code == 401
        assert [authority.id for authority in authorities.get_all()] == [1]


class TestApiDisabled:
    def test_cannot_clear_authorities(self, authorities: AuthorityRepository, client: FlaskClient) -> None:
        authorities.add(Authority(id_=1, name="Liverpool City Region Combined Authority"))

        response = client.delete("/authorities", headers={"Authorization": "API-Key boardman"})

        assert response.status_code == 401
        assert [authority.id for authority in authorities.get_all()] == [1]
