from flask.testing import FlaskClient

from tests.integration.pages import LandingPage


def test_landing(client: FlaskClient) -> None:
    landing_page = LandingPage(client).show()

    assert landing_page.visible()


def test_header_home_shows_landing(client: FlaskClient) -> None:
    landing_page = LandingPage(client).show()

    assert landing_page.header().home_url == "/"


def test_landing_when_authenticated_shows_home(client: FlaskClient) -> None:
    with client.session_transaction() as session:
        session["user"] = {"email": "user@domain.com"}

    response = client.get("/")

    assert response.status_code == 302 and response.location == "/home"
