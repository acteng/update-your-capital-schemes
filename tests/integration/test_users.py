from typing import Any, Mapping

import pytest
from flask.testing import FlaskClient

from schemes.domain.users import User, UserRepository


class TestUsersApi:
    @pytest.fixture(name="config", scope="class")
    @classmethod
    def config_fixture(cls, config: Mapping[str, Any]) -> Mapping[str, Any]:
        return dict(config) | {"API_KEY": "boardman"}

    def test_add_users(self, users: UserRepository, client: FlaskClient) -> None:
        response = client.post(
            "/users",
            headers={"Authorization": "API-Key boardman"},
            json=[
                {"email": "boardman@example.com", "authority_abbreviation": "LIV"},
                {"email": "obree@example.com", "authority_abbreviation": "WYO"},
            ],
        )

        assert response.status_code == 201
        user1 = users.get("boardman@example.com")
        user2 = users.get("obree@example.com")
        assert user1 and user1.email == "boardman@example.com" and user1.authority_abbreviation == "LIV"
        assert user2 and user2.email == "obree@example.com" and user2.authority_abbreviation == "WYO"

    def test_cannot_add_users_when_no_credentials(self, users: UserRepository, client: FlaskClient) -> None:
        response = client.post("/users", json=[{"email": "boardman@example.com", "authority_abbreviation": "LIV"}])

        assert response.status_code == 401
        assert not users.get("boardman@example.com")

    def test_cannot_add_users_when_incorrect_credentials(self, users: UserRepository, client: FlaskClient) -> None:
        response = client.post(
            "/users",
            headers={"Authorization": "API-Key obree"},
            json=[{"email": "boardman@example.com", "authority_abbreviation": "LIV"}],
        )

        assert response.status_code == 401
        assert not users.get("boardman@example.com")

    def test_cannot_add_users_with_invalid_repr(self, users: UserRepository, client: FlaskClient) -> None:
        response = client.post(
            "/users",
            headers={"Authorization": "API-Key boardman"},
            json=[{"email": "boardman@example.com", "authority_abbreviation": "LIV", "foo": "bar"}],
        )

        assert response.status_code == 400
        assert not users.get("boardman@example.com")

    def test_clear_users(self, users: UserRepository, client: FlaskClient) -> None:
        users.add(User("boardman@example.com", authority_abbreviation="LIV"))

        response = client.delete("/users", headers={"Authorization": "API-Key boardman"})

        assert response.status_code == 204
        assert not users.get("boardman@example.com")

    def test_cannot_clear_users_when_no_credentials(self, users: UserRepository, client: FlaskClient) -> None:
        users.add(User("boardman@example.com", authority_abbreviation="LIV"))

        response = client.delete("/users")

        assert response.status_code == 401
        assert users.get("boardman@example.com")

    def test_cannot_clear_users_when_incorrect_credentials(self, users: UserRepository, client: FlaskClient) -> None:
        users.add(User("boardman@example.com", authority_abbreviation="LIV"))

        response = client.delete("/users", headers={"Authorization": "API-Key obree"})

        assert response.status_code == 401
        assert users.get("boardman@example.com")


class TestUsersApiWhenDisabled:
    def test_cannot_add_users(self, users: UserRepository, client: FlaskClient) -> None:
        response = client.post(
            "/users",
            headers={"Authorization": "API-Key boardman"},
            json=[{"email": "boardman@example.com", "authority_abbreviation": "LIV"}],
        )

        assert response.status_code == 401
        assert not users.get("boardman@example.com")

    def test_cannot_clear_users(self, users: UserRepository, client: FlaskClient) -> None:
        users.add(User("boardman@example.com", authority_abbreviation="LIV"))

        response = client.delete("/users", headers={"Authorization": "API-Key boardman"})

        assert response.status_code == 401
        assert users.get("boardman@example.com")
