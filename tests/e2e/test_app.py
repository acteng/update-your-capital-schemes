import pytest
from flask import Flask
from playwright.sync_api import Page, expect


@pytest.mark.usefixtures("live_server")
def test_index(app: Flask, page: Page) -> None:
    page.goto(f"{_get_base_url(app)}")

    expect(page.get_by_role("heading")).to_contain_text("Schemes")


def _get_base_url(app: Flask) -> str:
    scheme = app.config["PREFERRED_URL_SCHEME"]
    server_name = app.config["SERVER_NAME"]
    root = app.config["APPLICATION_ROOT"]
    return f"{scheme}://{server_name}{root}"
