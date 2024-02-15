import pytest
from flask.testing import FlaskClient
from playwright.sync_api import Page

from tests.e2e.page_adapter import FlaskPage
from tests.e2e.pages import StartPage


class TestStart:
    @pytest.fixture(name="page")
    def page_fixture(self, client: FlaskClient) -> Page:
        return FlaskPage(client)

    def test_start(self, page: Page) -> None:
        start_page = StartPage.open(page)

        assert start_page.is_visible

    def test_header_home_shows_start(self, page: Page) -> None:
        start_page = StartPage.open(page)

        assert start_page.header.home_url == "/"

    def test_start_when_authenticated_shows_schemes(self, client: FlaskClient) -> None:
        with client.session_transaction() as session:
            session["user"] = {"email": "boardman@example.com"}

        response = client.get("/")

        assert response.status_code == 302 and response.location == "/schemes"
