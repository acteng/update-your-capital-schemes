import pytest
from flask import Flask
from playwright.sync_api import Page, expect

from tests.e2e.pages import LandingPage


@pytest.mark.usefixtures("live_server")
def test_index(app: Flask, page: Page) -> None:
    landing_page = LandingPage(app, page).open()

    expect(landing_page.header).to_contain_text("Schemes")
