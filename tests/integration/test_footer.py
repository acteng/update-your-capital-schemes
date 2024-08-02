from flask.testing import FlaskClient

from tests.integration.pages import StartPage


class TestFooter:
    def test_privacy_shows_privacy(self, client: FlaskClient) -> None:
        start_page = StartPage.open(client)

        assert start_page.footer.privacy_url == "/privacy"

    def test_accessibility_shows_accessibility(self, client: FlaskClient) -> None:
        start_page = StartPage.open(client)

        assert start_page.footer.accessibility_url == "/accessibility"

    def test_cookies_shows_cookies(self, client: FlaskClient) -> None:
        start_page = StartPage.open(client)

        assert start_page.footer.cookies_url == "/cookies"
