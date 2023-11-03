from __future__ import annotations

import re
from typing import Iterator, cast

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

    def header(self) -> ServiceHeaderComponent:
        return ServiceHeaderComponent(cast(Tag, self._soup.header))

    def authority(self) -> str:
        return (self._soup.main.h1.string if self._soup.main and self._soup.main.h1 else None) or ""

    def schemes(self) -> SchemesTableComponent:
        return SchemesTableComponent(cast(Tag, cast(Tag, self._soup.main).table))


class ServiceHeaderComponent:
    def __init__(self, tag: Tag):
        self.home_url = cast(Tag, tag.find("a", class_="one-login-header__link"))["href"]
        self.profile_url = cast(Tag, tag.find("a", class_="one-login-header__nav__link"))["href"]
        self.sign_out_url = cast(Tag, tag.find("a", string=re.compile("Sign out")))["href"]


class SchemesTableComponent:
    def __init__(self, tag: Tag):
        self._rows = tag.tbody.find_all("tr") if tag.tbody else []

    def __iter__(self) -> Iterator[dict[str, str]]:
        return iter([SchemeRowComponent(row).to_dict() for row in self._rows])


class SchemeRowComponent:
    def __init__(self, tag: Tag):
        cells = tag.find_all("td")
        self.reference = cells[0].string
        self.name = cells[1].string

    def to_dict(self) -> dict[str, str]:
        return {"reference": self.reference, "name": self.name}
