from typing import Any, Mapping

import inject
import pytest
from flask.testing import FlaskClient

from schemes.users import User, UserRepository


@pytest.fixture(name="users")
def users_fixture() -> UserRepository:
    return inject.instance(UserRepository)


def test_add_users(users: UserRepository, client: FlaskClient) -> None:
    response = client.post("/users", json=[{"email": "boardman@example.com"}, {"email": "obree@example.com"}])

    assert response.status_code == 201
    assert users.get_all() == [User("boardman@example.com"), User("obree@example.com")]


def test_clear_users(users: UserRepository, client: FlaskClient) -> None:
    users.add(User("boardman@example.com"))

    response = client.delete("/users")

    assert response.status_code == 204
    assert not users.get_all()


class TestProduction:
    @pytest.fixture(name="config")
    def config_fixture(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        return config | {"TESTING": False}

    def test_cannot_add_user(self, client: FlaskClient) -> None:
        response = client.post("/users", json={"email": "boardman@example.com"})

        assert response.status_code == 404
