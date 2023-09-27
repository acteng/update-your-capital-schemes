import pytest
from flask import Flask
from playwright.sync_api import Page, expect

from tests.e2e.pages import HomePage


@pytest.mark.usefixtures("live_server")
def test_index(app: Flask, page: Page) -> None:
    home_page = HomePage(app, page).open()

    expect(home_page.header).to_contain_text("Home")
