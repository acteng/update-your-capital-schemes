from typing import Any, Mapping

import pytest
from flask.testing import FlaskClient


class TestBasicAuthWhenUnauthenticated:
    def test_access_when_no_basic_auth(self, client: FlaskClient) -> None:
        response = client.get("/")

        assert response.status_code == 200


class TestBasicAuthWhenAuthenticated:
    @pytest.fixture(name="config")
    def config_fixture(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        return dict(config) | {"BASIC_AUTH_USERNAME": "boardman", "BASIC_AUTH_PASSWORD": "letmein"}

    def test_challenge_when_basic_auth(self, client: FlaskClient) -> None:
        response = client.get("/")

        assert response.status_code == 401 and response.headers["WWW-Authenticate"] == "Basic realm='Schemes'"

    def test_access_when_basic_auth(self, client: FlaskClient) -> None:
        # echo -n 'boardman:letmein' | base64
        response = client.get("/", headers={"Authorization": "Basic Ym9hcmRtYW46bGV0bWVpbg=="})

        assert response.status_code == 200

    def test_cannot_access_when_incorrect_basic_auth(self, client: FlaskClient) -> None:
        # echo -n 'obree:opensesame' | base64
        response = client.get("/", headers={"Authorization": "Basic b2JyZWU6b3BlbnNlc2FtZQ=="})

        assert response.status_code == 401 and response.text == "Unauthorized"
