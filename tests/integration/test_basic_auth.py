from flask.testing import FlaskClient
from schemes import create_app


def test_access_when_no_basic_auth(client: FlaskClient) -> None:
    response = client.get("/")

    assert response.status_code == 200


def test_challenge_when_basic_auth() -> None:
    client = _create_test_client("alice", "letmein")

    response = client.get("/")

    assert response.status_code == 401 and response.headers["WWW-Authenticate"] == "Basic realm='Schemes'"


def test_access_when_basic_auth() -> None:
    client = _create_test_client("alice", "letmein")

    # echo -n 'alice:letmein' | base64
    response = client.get("/", headers={"Authorization": "Basic YWxpY2U6bGV0bWVpbg=="})

    assert response.status_code == 200


def test_cannot_access_when_incorrect_basic_auth() -> None:
    client = _create_test_client("alice", "letmein")

    # echo -n 'bob:opensesame' | base64
    response = client.get("/", headers={"Authorization": "Basic Ym9iOm9wZW5zZXNhbWU="})

    assert response.status_code == 401 and response.text == "Unauthorized"


def _create_test_client(username: str, password: str) -> FlaskClient:
    app = create_app({"BASIC_AUTH_USERNAME": username, "BASIC_AUTH_PASSWORD": password})
    return app.test_client()
