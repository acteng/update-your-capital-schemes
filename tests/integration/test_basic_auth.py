import base64

from flask.testing import FlaskClient
from schemes import create_app


def test_access_when_no_basic_auth(client: FlaskClient) -> None:
    response = client.get("/")

    assert response.status_code == 200


def test_challenge_when_basic_auth() -> None:
    client = _create_test_client("alice", "letmein")

    response = client.get("/")

    assert response.status_code == 401 \
        and response.headers["WWW-Authenticate"] == "Basic realm='Schemes'"


def test_access_when_basic_auth() -> None:
    username, password = "alice", "letmein"
    client = _create_test_client(username, password)

    response = client.get("/", headers={"Authorization": f"Basic {_create_b64_auth(username, password)}"})

    assert response.status_code == 200


def test_cannot_access_when_incorrect_basic_auth() -> None:
    client = _create_test_client("alice", "letmein")

    response = client.get("/", headers={"Authorization": f"Basic {_create_b64_auth('bob','opensesame')}"})

    assert response.status_code == 401 and response.text == "Unauthorized"


def _create_test_client(username: str, password: str) -> FlaskClient:
    app = create_app({
        "BASIC_AUTH_USERNAME": username,
        "BASIC_AUTH_PASSWORD": password
    })
    return app.test_client()

def _create_b64_auth(username: str, password: str) -> str:
    auth_details = ":".join([username, password])
    b64_bytes = base64.b64encode(auth_details.encode())
    return b64_bytes.decode()
