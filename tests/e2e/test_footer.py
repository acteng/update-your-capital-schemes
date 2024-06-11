import pytest
from playwright.sync_api import Page

from tests.e2e.pages import StartPage


@pytest.mark.usefixtures("live_server")
def test_cookies(page: Page) -> None:
    start_page = StartPage.open(page)

    cookies_page = start_page.footer.cookies()

    assert cookies_page.is_visible