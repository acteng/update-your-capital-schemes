from typing import Any, Mapping

import inject
import pytest
from flask import Flask
from flask.testing import FlaskClient

from schemes.authorities.domain import Authority
from schemes.authorities.services import AuthorityRepository
from schemes.schemes.domain import FundingProgramme, Scheme, SchemeType
from schemes.schemes.services import SchemeRepository
from schemes.users.domain import User
from schemes.users.services import UserRepository


@pytest.fixture(name="authorities")
def authorities_fixture(app: Flask) -> AuthorityRepository:  # pylint: disable=unused-argument
    return inject.instance(AuthorityRepository)


@pytest.fixture(name="users")
def users_fixture(app: Flask) -> UserRepository:  # pylint: disable=unused-argument
    return inject.instance(UserRepository)


@pytest.fixture(name="schemes")
def schemes_fixture(app: Flask) -> SchemeRepository:  # pylint: disable=unused-argument
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
        assert [_authority_to_tuple(authority) for authority in authorities.get_all()] == [
            _authority_to_tuple(Authority(id_=1, name="Liverpool City Region Combined Authority")),
            _authority_to_tuple(Authority(id_=2, name="West Yorkshire Combined Authority")),
        ]

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
        assert [_user_to_tuple(user) for user in users.get_all()] == [
            _user_to_tuple(User("boardman@example.com", authority_id=1)),
            _user_to_tuple(User("obree@example.com", authority_id=1)),
        ]

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
        wirral_package = Scheme(id_=1, name="Wirral Package", authority_id=1)
        wirral_package.type = SchemeType.CONSTRUCTION
        wirral_package.funding_programme = FundingProgramme.ATF4
        assert [_scheme_to_tuple(scheme) for scheme in schemes.get_all()] == [
            _scheme_to_tuple(wirral_package),
            _scheme_to_tuple(Scheme(id_=2, name="School Streets", authority_id=1)),
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


def _authority_to_tuple(authority: Authority | None) -> tuple[int, str] | None:
    return (authority.id, authority.name) if authority else None


def _user_to_tuple(user: User | None) -> tuple[str, int] | None:
    return (user.email, user.authority_id) if user else None


def _scheme_to_tuple(scheme: Scheme | None) -> tuple[int, str, int, SchemeType | None, FundingProgramme | None] | None:
    return (scheme.id, scheme.name, scheme.authority_id, scheme.type, scheme.funding_programme) if scheme else None
