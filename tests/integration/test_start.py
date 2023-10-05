from flask.testing import FlaskClient

from tests.integration.pages import StartPage


def test_start(client: FlaskClient) -> None:
    start_page = StartPage(client).show()

    assert start_page.visible()


def test_header_home_shows_start(client: FlaskClient) -> None:
    start_page = StartPage(client).show()

    assert start_page.header().home_url == "/"


def test_start_when_authenticated_shows_home(client: FlaskClient) -> None:
    with client.session_transaction() as session:
        session["user"] = {"email": "user@domain.com"}

    response = client.get("/")

    assert response.status_code == 302 and response.location == "/home"
