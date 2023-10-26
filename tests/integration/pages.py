from __future__ import annotations

import re
from typing import cast

from bs4 import BeautifulSoup, Tag
from flask.testing import FlaskClient
from werkzeug import Response as BaseResponse


class StartPage:
    def __init__(self, client: FlaskClient):
        self._client = client
        self._soup = BeautifulSoup()

    def open(self) -> StartPage:
        response = self._client.get("/")
        self._soup = BeautifulSoup(response.text, "html.parser")
        return self

    def visible(self) -> bool:
        return self._soup.h1.string == "Schemes" if self._soup.h1 else False

    def header(self) -> HeaderComponent:
        return HeaderComponent(cast(Tag, self._soup.header))


class HeaderComponent:
    def __init__(self, tag: Tag):
        self.home_url = cast(Tag, tag.find("a", class_="govuk-header__link"))["href"]


class UnauthorizedPage:
    def __init__(self, client: FlaskClient):
        self._client = client
        self._response = BaseResponse()
        self._soup = BeautifulSoup()

    def open(self) -> UnauthorizedPage:
        self._response = self._client.get("/auth/unauthorized")
        self._soup = BeautifulSoup(self._response.text, "html.parser")
        return self

    def visible(self) -> bool:
        return self._soup.h1.string == "Unauthorised" if self._soup.h1 else False

    def is_unauthorized(self) -> bool:
        return self._response.status_code == 401


class SchemesPage:
    def __init__(self, client: FlaskClient):
        self._client = client
        self._soup = BeautifulSoup()

    def open(self) -> SchemesPage:
        response = self._client.get("/schemes")
        self._soup = BeautifulSoup(response.text, "html.parser")
        return self

    def visible(self) -> bool:
        return self._soup.h1.string == "Home" if self._soup.h1 else False

    def header(self) -> ServiceHeaderComponent:
        return ServiceHeaderComponent(cast(Tag, self._soup.header))


class ServiceHeaderComponent:
    def __init__(self, tag: Tag):
        self.home_url = cast(Tag, tag.find("a", class_="one-login-header__link"))["href"]
        self.profile_url = cast(Tag, tag.find("a", class_="one-login-header__nav__link"))["href"]
        self.sign_out_url = cast(Tag, tag.find("a", string=re.compile("Sign out")))["href"]
