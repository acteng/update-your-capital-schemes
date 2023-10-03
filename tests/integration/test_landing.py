from flask.testing import FlaskClient

from tests.integration.pages import LandingPage


def test_index(client: FlaskClient) -> None:
    response = client.get("/")

    assert LandingPage(response.text).header == "Schemes"


def test_landing_when_authenticated_shows_home(client: FlaskClient) -> None:
    with client.session_transaction() as session:
        session["user"] = {"email": "user@domain.com"}

    response = client.get("/")

    assert response.status_code == 302 and response.location == "/home"
