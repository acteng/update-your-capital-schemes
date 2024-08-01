from flask.testing import FlaskClient

from tests.integration.pages import CookiesPage, PrivacyPage


class TestLegal:
    def test_privacy(self, client: FlaskClient) -> None:
        privacy_page = PrivacyPage.open(client)

        assert privacy_page.is_visible
        assert privacy_page.title == "Privacy notice - Update your capital schemes - Active Travel England - GOV.UK"

    def test_cookies(self, client: FlaskClient) -> None:
        cookies_page = CookiesPage.open(client)

        assert cookies_page.is_visible
