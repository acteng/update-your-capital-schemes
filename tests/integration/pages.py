from __future__ import annotations

from typing import cast

from bs4 import BeautifulSoup, Tag
from flask.testing import FlaskClient


class LandingPage:
    def __init__(self, client: FlaskClient):
        self._client = client
        self._soup = BeautifulSoup()

    def show(self) -> LandingPage:
        response = self._client.get("/")
        self._soup = BeautifulSoup(response.text, "html.parser")
        return self

    def visible(self) -> bool:
        return self._soup.h1.string == "Schemes" if self._soup.h1 else False

    def header(self) -> Header:
        return Header(cast(Tag, self._soup.header))


class Header:
    def __init__(self, tag: Tag):
        self.home_url = cast(Tag, tag.find("a", class_="govuk-header__link"))["href"]


class HomePage:
    def __init__(self, client: FlaskClient):
        self._client = client
        self._soup = BeautifulSoup()

    def show(self) -> HomePage:
        response = self._client.get("/home")
        self._soup = BeautifulSoup(response.text, "html.parser")
        return self

    def visible(self) -> bool:
        return self._soup.h1.string == "Home" if self._soup.h1 else False
