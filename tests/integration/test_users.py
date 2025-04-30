from typing import Any, Mapping

import pytest
from flask.testing import FlaskClient

from schemes.domain.users import User, UserRepository


class TestUsersApi:
    @pytest.fixture(name="config", scope="class")
    def config_fixture(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        return dict(config) | {"API_KEY": "boardman"}

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
    def test_cannot_clear_users(self, users: UserRepository, client: FlaskClient) -> None:
        users.add(User("boardman@example.com", authority_abbreviation="LIV"))

        response = client.delete("/users", headers={"Authorization": "API-Key boardman"})

        assert response.status_code == 401
        assert users.get("boardman@example.com")
