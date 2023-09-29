from typing import Any, Mapping

import pytest
from flask.testing import FlaskClient


class TestUnauthenticated:
    def test_access_when_no_basic_auth(self, client: FlaskClient) -> None:
        response = client.get("/")

        assert response.status_code == 200


class TestAuthenticated:
    @pytest.fixture(name="config")
    def config_fixture(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        return config | {"BASIC_AUTH_USERNAME": "alice", "BASIC_AUTH_PASSWORD": "letmein"}

    def test_challenge_when_basic_auth(self, client: FlaskClient) -> None:
        response = client.get("/")

        assert response.status_code == 401 and response.headers["WWW-Authenticate"] == "Basic realm='Schemes'"

    def test_access_when_basic_auth(self, client: FlaskClient) -> None:
        # echo -n 'alice:letmein' | base64
        response = client.get("/", headers={"Authorization": "Basic YWxpY2U6bGV0bWVpbg=="})

        assert response.status_code == 200

    def test_cannot_access_when_incorrect_basic_auth(self, client: FlaskClient) -> None:
        # echo -n 'bob:opensesame' | base64
        response = client.get("/", headers={"Authorization": "Basic Ym9iOm9wZW5zZXNhbWU="})

        assert response.status_code == 401 and response.text == "Unauthorized"
