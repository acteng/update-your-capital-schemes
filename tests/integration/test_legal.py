from flask.testing import FlaskClient

from tests.integration.pages import AccessibilityPage, CookiesPage, PrivacyPage


class TestLegal:
    def test_privacy(self, client: FlaskClient) -> None:
        privacy_page = PrivacyPage.open(client)

        assert privacy_page.is_visible
        assert privacy_page.title == "Privacy notice - Update your capital schemes - Active Travel England - GOV.UK"

    def test_accessibility(self, client: FlaskClient) -> None:
        accessibility_page = AccessibilityPage.open(client)

        assert accessibility_page.is_visible
        assert (
            accessibility_page.title
            == "Accessibility statement - Update your capital schemes - Active Travel England - GOV.UK"
        )

    def test_cookies(self, client: FlaskClient) -> None:
        cookies_page = CookiesPage.open(client)

        assert cookies_page.is_visible
        assert cookies_page.title == "Cookies - Update your capital schemes - Active Travel England - GOV.UK"

    def test_security(self, client: FlaskClient) -> None:
        response = client.get("/.well-known/security.txt")

        assert response.status_code == 200 and response.content_type == "text/plain; charset=utf-8"
