from typing import Any, Mapping

import pytest
from flask.testing import FlaskClient

from schemes.domain.authorities import Authority, AuthorityRepository
from schemes.domain.users import UserRepository


class TestAuthoritiesApi:
    @pytest.fixture(name="config", scope="class")
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


class TestAuthoritiesApiWhenDisabled:
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

    def test_cannot_clear_authorities(self, authorities: AuthorityRepository, client: FlaskClient) -> None:
        authorities.add(Authority(id_=1, name="Liverpool City Region Combined Authority"))

        response = client.delete("/authorities", headers={"Authorization": "API-Key boardman"})

        assert response.status_code == 401
        assert authorities.get(1)
