from flask.testing import FlaskClient

from tests.integration.pages import StartPage


class TestStart:
    def test_start(self, client: FlaskClient) -> None:
        start_page = StartPage.open(client)

        assert start_page.is_visible

    def test_start_when_authenticated_shows_schemes(self, client: FlaskClient) -> None:
        with client.session_transaction() as session:
            session["user"] = {"email": "boardman@example.com"}

        response = client.get("/")

        assert response.status_code == 302 and response.location == "/schemes"
