import pytest
from playwright.async_api import Page

from tests.e2e.pages import StartPage

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest.mark.usefixtures("live_server")
async def test_privacy(page: Page) -> None:
    start_page = await StartPage.open(page)

    privacy_page = await start_page.footer.privacy()

    assert await privacy_page.is_visible()


@pytest.mark.usefixtures("live_server")
async def test_accessibility(page: Page) -> None:
    start_page = await StartPage.open(page)

    accessibility_page = await start_page.footer.accessibility()

    assert await accessibility_page.is_visible()


@pytest.mark.usefixtures("live_server")
async def test_cookies(page: Page) -> None:
    start_page = await StartPage.open(page)

    cookies_page = await start_page.footer.cookies()

    assert await cookies_page.is_visible()
