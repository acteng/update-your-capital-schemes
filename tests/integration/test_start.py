from flask.testing import FlaskClient

from tests.integration.pages import StartPage


def test_start(client: FlaskClient) -> None:
    start_page = StartPage(client).open()

    assert start_page.is_visible()


def test_header_home_shows_start(client: FlaskClient) -> None:
    start_page = StartPage(client).open()

    assert start_page.header().home_url == "/"


def test_start_when_authenticated_shows_schemes(client: FlaskClient) -> None:
    with client.session_transaction() as session:
        session["user"] = {"email": "boardman@example.com"}

    response = client.get("/")

    assert response.status_code == 302 and response.location == "/schemes"
