from typing import Any, Mapping

import pytest
from flask import current_app
from flask.testing import FlaskClient

from schemes.users import User


def test_add_user(client: FlaskClient) -> None:
    response = client.post("/api/users", json={"email": "boardman@example.com"})

    assert response.status_code == 201
    assert current_app.extensions["users"].get("boardman@example.com")


def test_clear_users(client: FlaskClient) -> None:
    current_app.extensions["users"].add(User("boardman@example.com"))

    response = client.delete("/api/users")

    assert response.status_code == 204
    assert not current_app.extensions["users"].get_all()


class TestProduction:
    @pytest.fixture(name="config")
    def config_fixture(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        return config | {"TESTING": False}

    def test_cannot_add_user(self, client: FlaskClient) -> None:
        response = client.post("/api/users", json={"email": "boardman@example.com"})

        assert response.status_code == 404
