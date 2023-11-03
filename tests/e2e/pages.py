from __future__ import annotations

from typing import Iterator

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

    def open_when_authenticated(self) -> SchemesPage:
        self.open()
        return SchemesPage(self._app, self._page)

    @property
    def is_visible(self) -> bool:
        return self._page.get_by_role("heading", name="Schemes").is_visible()

    def start(self) -> SchemesPage:
        self._start.click()
        return SchemesPage(self._app, self._page)

    def start_when_unauthenticated(self) -> LoginPage:
        self.start()
        return LoginPage(self._app, self._page)


class LoginPage:
    def __init__(self, app: Flask, page: Page):
        self._app = app
        self._page = page

    @property
    def is_visible(self) -> bool:
        return self._page.get_by_role("heading", name="Login").is_visible()


class UnauthorizedPage:
    def __init__(self, app: Flask, page: Page):
        self._app = app
        self._page = page

    @property
    def is_visible(self) -> bool:
        return self._page.get_by_role("heading", name="Unauthorised").is_visible()


class SchemesPage:
    def __init__(self, app: Flask, page: Page):
        self._app = app
        self._page = page
        self.header = ServiceHeaderComponent(app, page.get_by_role("banner"))
        self._main = page.get_by_role("main")
        self._authority = self._main.get_by_role("heading")
        self.schemes = SchemesTableComponent(self._main.get_by_role("table"))

    def open(self) -> SchemesPage:
        self._page.goto(f"{_get_base_url(self._app)}/schemes")
        return self

    def open_when_unauthenticated(self) -> LoginPage:
        self.open()
        return LoginPage(self._app, self._page)

    def open_when_unauthorized(self) -> UnauthorizedPage:
        self.open()
        return UnauthorizedPage(self._app, self._page)

    @property
    def authority(self) -> str:
        return self._authority.text_content() or ""


class ServiceHeaderComponent:
    def __init__(self, app: Flask, component: Locator):
        self._app = app
        self._component = component

    def sign_out(self) -> StartPage:
        self._component.get_by_role("link", name="Sign out").click()
        return StartPage(self._app, self._component.page)


class SchemesTableComponent:
    def __init__(self, component: Locator):
        self._rows = component.get_by_role("row")

    def __iter__(self) -> Iterator[dict[str, str]]:
        return iter([SchemeRowComponent(row).to_dict() for row in self._rows.all()[1:]])


class SchemeRowComponent:
    def __init__(self, component: Locator):
        cells = component.get_by_role("cell")
        self._reference = cells.nth(0)
        self._name = cells.nth(1)

    def to_dict(self) -> dict[str, str]:
        return {"reference": self._reference.text_content() or "", "name": self._name.text_content() or ""}


def _get_base_url(app: Flask) -> str:
    scheme = app.config["PREFERRED_URL_SCHEME"]
    server_name = app.config["SERVER_NAME"]
    root = app.config["APPLICATION_ROOT"]
    return f"{scheme}://{server_name}{root}"
