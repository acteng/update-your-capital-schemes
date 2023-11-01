from typing import Any, Mapping

import inject
import pytest
from flask import Flask
from flask.testing import FlaskClient

from schemes.users.domain import User
from schemes.users.services import UserRepository


@pytest.fixture(name="users")
def users_fixture(app: Flask) -> UserRepository:  # pylint: disable=unused-argument
    return inject.instance(UserRepository)


class TestApiEnabled:
    @pytest.fixture(name="config")
    def config_fixture(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        return config | {"API_KEY": "boardman"}

    def test_clear_users(self, users: UserRepository, client: FlaskClient) -> None:
        users.add(User("boardman@example.com", authority_id=1))

        response = client.delete("/users", headers={"Authorization": "API-Key boardman"})

        assert response.status_code == 204
        assert not users.get_all()

    def test_cannot_clear_users_when_no_credentials(self, users: UserRepository, client: FlaskClient) -> None:
        users.add(User("boardman@example.com", authority_id=1))

        response = client.delete("/users")

        assert response.status_code == 401
        assert users.get_all() == [User("boardman@example.com", authority_id=1)]

    def test_cannot_clear_users_when_incorrect_credentials(self, users: UserRepository, client: FlaskClient) -> None:
        users.add(User("boardman@example.com", authority_id=1))

        response = client.delete("/users", headers={"Authorization": "API-Key obree"})

        assert response.status_code == 401
        assert users.get_all() == [User("boardman@example.com", authority_id=1)]


class TestApiDisabled:
    def test_cannot_clear_users(self, users: UserRepository, client: FlaskClient) -> None:
        users.add(User("boardman@example.com", authority_id=1))

        response = client.delete(
            "/users", headers={"Authorization": "API-Key boardman"}, json=[{"email": "boardman@example.com"}]
        )

        assert response.status_code == 401
        assert users.get_all() == [User("boardman@example.com", authority_id=1)]
