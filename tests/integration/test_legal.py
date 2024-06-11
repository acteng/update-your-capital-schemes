from flask.testing import FlaskClient

from tests.integration.pages import CookiesPage


class TestLegal:
    def test_cookies(self, client: FlaskClient) -> None:
        cookies_page = CookiesPage.open(client)

        assert cookies_page.is_visible
