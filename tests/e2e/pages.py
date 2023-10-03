from __future__ import annotations

from flask import Flask
from playwright.sync_api import Page


class LandingPage:
    def __init__(self, app: Flask, page: Page):
        self._app = app
        self._page = page
        self.header = page.get_by_role("heading").first
        self._start = page.get_by_role("button")

    def open(self) -> LandingPage:
        self._page.goto(f"{_get_base_url(self._app)}")
        return self

    def open_when_authenticated(self) -> HomePage:
        self.open()
        return HomePage(self._app, self._page)

    def start(self) -> HomePage:
        self._start.click()
        return HomePage(self._app, self._page)

    def start_when_unauthenticated(self) -> LoginPage:
        self.start()
        return LoginPage(self._app, self._page)


class HomePage:
    def __init__(self, app: Flask, page: Page):
        self._app = app
        self._page = page
        self.header = page.get_by_role("heading").first

    def open(self) -> HomePage:
        self._page.goto(f"{_get_base_url(self._app)}/home")
        return self

    def open_when_unauthenticated(self) -> LoginPage:
        self.open()
        return LoginPage(self._app, self._page)

    def visible(self) -> bool:
        return self.header.text_content() == "Home"


class LoginPage:
    def __init__(self, app: Flask, page: Page):
        self._app = app
        self._page = page
        self.header = page.get_by_role("heading").first

    def visible(self) -> bool:
        return self.header.text_content() == "Login"


def _get_base_url(app: Flask) -> str:
    scheme = app.config["PREFERRED_URL_SCHEME"]
    server_name = app.config["SERVER_NAME"]
    root = app.config["APPLICATION_ROOT"]
    return f"{scheme}://{server_name}{root}"
