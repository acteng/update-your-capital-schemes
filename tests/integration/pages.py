from __future__ import annotations

from bs4 import BeautifulSoup
from flask.testing import FlaskClient


class LandingPage:
    def __init__(self, client: FlaskClient):
        self._client = client
        self._soup: BeautifulSoup | None = None

    def show(self) -> LandingPage:
        response = self._client.get("/")
        self._soup = BeautifulSoup(response.text, "html.parser")
        return self

    def visible(self) -> bool:
        return self._soup.h1.string == "Schemes" if self._soup and self._soup.h1 else False


class HomePage:
    def __init__(self, client: FlaskClient):
        self._client = client
        self._soup: BeautifulSoup | None = None

    def show(self) -> HomePage:
        response = self._client.get("/home")
        self._soup = BeautifulSoup(response.text, "html.parser")
        return self

    def visible(self) -> bool:
        return self._soup.h1.string == "Home" if self._soup and self._soup.h1 else False
