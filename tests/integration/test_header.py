from flask.testing import FlaskClient

from tests.integration.pages import StartPage


class TestHeader:
    def test_home_shows_start(self, client: FlaskClient) -> None:
        start_page = StartPage.open(client)

        assert start_page.header.home_url == "/"
