from __future__ import annotations

from flask import Flask
from playwright.sync_api import Locator, Page


class StartPage:
    def __init__(self, app: Flask, page: Page):
        self._app = app
        self._page = page
        self._start = page.get_by_role("button")

    def open(self) -> StartPage:
        self._page.goto(f"{_get_base_url(self._app)}")
        return self

    def open_when_authenticated(self) -> HomePage:
        self.open()
        return HomePage(self._app, self._page)

    def visible(self) -> bool:
        return self._page.get_by_role("heading", name="Schemes").is_visible()

    def start(self) -> HomePage:
        self._start.click()
        return HomePage(self._app, self._page)

    def start_when_unauthenticated(self) -> LoginPage:
        self.start()
        return LoginPage(self._app, self._page)


class LoginPage:
    def __init__(self, app: Flask, page: Page):
        self._app = app
        self._page = page

    def visible(self) -> bool:
        return self._page.get_by_role("heading", name="Login").is_visible()


class UnauthorizedPage:
    def __init__(self, app: Flask, page: Page):
        self._app = app
        self._page = page

    def visible(self) -> bool:
        return self._page.get_by_role("heading", name="Unauthorised").is_visible()


class HomePage:
    def __init__(self, app: Flask, page: Page):
        self._app = app
        self._page = page
        self.header = ServiceHeaderComponent(app, page.get_by_role("banner"))

    def open(self) -> HomePage:
        self._page.goto(f"{_get_base_url(self._app)}/home")
        return self

    def open_when_unauthenticated(self) -> LoginPage:
        self.open()
        return LoginPage(self._app, self._page)

    def open_when_unauthorized(self) -> UnauthorizedPage:
        self.open()
        return UnauthorizedPage(self._app, self._page)

    def visible(self) -> bool:
        return self._page.get_by_role("heading", name="Home").is_visible()


class ServiceHeaderComponent:
    def __init__(self, app: Flask, component: Locator):
        self._app = app
        self._component = component

    def sign_out(self) -> StartPage:
        self._component.get_by_role("link", name="Sign out").click()
        return StartPage(self._app, self._component.page)


def _get_base_url(app: Flask) -> str:
    scheme = app.config["PREFERRED_URL_SCHEME"]
    server_name = app.config["SERVER_NAME"]
    root = app.config["APPLICATION_ROOT"]
    return f"{scheme}://{server_name}{root}"
