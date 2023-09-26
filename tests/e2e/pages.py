from __future__ import annotations

from flask import Flask
from playwright.sync_api import Page


class LandingPage:
    def __init__(self, app: Flask, page: Page):
        self._base_url = _get_base_url(app)
        self._page = page
        self.header = page.get_by_role("heading").first

    def open(self) -> LandingPage:
        self._page.goto(f"{self._base_url}")
        return self


def _get_base_url(app: Flask) -> str:
    scheme = app.config["PREFERRED_URL_SCHEME"]
    server_name = app.config["SERVER_NAME"]
    root = app.config["APPLICATION_ROOT"]
    return f"{scheme}://{server_name}{root}"
