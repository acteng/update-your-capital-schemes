from flask.testing import FlaskClient

from tests.integration.pages import StartPage


class TestFooter:
    def test_cookies_shows_cookies(self, client: FlaskClient) -> None:
        start_page = StartPage.open(client)

        assert start_page.footer.cookies_url == "/cookies"