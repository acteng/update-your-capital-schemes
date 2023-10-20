from typing import Any, Mapping

import inject
import pytest
from flask.testing import FlaskClient

from schemes.users import User, UserRepository

BOARDMAN = "Basic Ym9hcmRtYW46bGV0bWVpbg=="  # echo -n 'boardman:letmein' | base64
OBREE = "Basic b2JyZWU6b3BlbnNlc2FtZQ=="  # echo -n 'obree:opensesame' | base64


@pytest.fixture(name="config")
def config_fixture(config: Mapping[str, Any]) -> Mapping[str, Any]:
    return config | {"API_USERNAME": "boardman", "API_PASSWORD": "letmein"}


@pytest.fixture(name="users")
def users_fixture() -> UserRepository:
    return inject.instance(UserRepository)


def test_add_users(users: UserRepository, client: FlaskClient) -> None:
    response = client.post(
        "/users",
        headers={"Authorization": BOARDMAN},
        json=[{"email": "boardman@example.com"}, {"email": "obree@example.com"}],
    )

    assert response.status_code == 201
    assert users.get_all() == [User("boardman@example.com"), User("obree@example.com")]


def test_cannot_add_users_when_no_credentials(users: UserRepository, client: FlaskClient) -> None:
    response = client.post("/users", json=[{"email": "boardman@example.com"}])

    assert response.status_code == 401
    assert not users.get_all()


def test_cannot_add_users_when_incorrect_credentials(users: UserRepository, client: FlaskClient) -> None:
    response = client.post("/users", headers={"Authorization": OBREE}, json=[{"email": "boardman@example.com"}])

    assert response.status_code == 401
    assert not users.get_all()


def test_clear_users(users: UserRepository, client: FlaskClient) -> None:
    users.add(User("boardman@example.com"))

    response = client.delete("/users", headers={"Authorization": BOARDMAN})

    assert response.status_code == 204
    assert not users.get_all()


def test_cannot_clear_users_when_no_credentials(users: UserRepository, client: FlaskClient) -> None:
    users.add(User("boardman@example.com"))

    response = client.delete("/users")

    assert response.status_code == 401
    assert users.get_all() == [User("boardman@example.com")]


def test_cannot_clear_users_when_incorrect_credentials(users: UserRepository, client: FlaskClient) -> None:
    users.add(User("boardman@example.com"))

    response = client.delete("/users", headers={"Authorization": OBREE})

    assert response.status_code == 401
    assert users.get_all() == [User("boardman@example.com")]


class TestProduction:
    @pytest.fixture(name="config")
    def config_fixture(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        return config | {"TESTING": False}

    def test_cannot_add_user(self, client: FlaskClient) -> None:
        response = client.post("/users", json={"email": "boardman@example.com"})

        assert response.status_code == 404
