from __future__ import annotations

from typing import Iterator

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

    @property
    def is_visible(self) -> bool:
        heading = self._soup.select_one("main h1")
        return heading.string == "Schemes" if heading else False

    @property
    def header(self) -> HeaderComponent:
        header_ = self._soup.select_one("header")
        assert header_
        return HeaderComponent(header_)


class HeaderComponent:
    def __init__(self, tag: Tag):
        home = tag.select_one("a.govuk-header__link")
        self.home_url = home["href"] if home else None


class UnauthorizedPage:
    def __init__(self, client: FlaskClient):
        self._client = client
        self._response = BaseResponse()
        self._soup = BeautifulSoup()

    def open(self) -> UnauthorizedPage:
        self._response = self._client.get("/auth/unauthorized")
        self._soup = BeautifulSoup(self._response.text, "html.parser")
        return self

    @property
    def is_visible(self) -> bool:
        heading = self._soup.select_one("main h1")
        return heading.string == "Unauthorised" if heading else False

    @property
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

    @property
    def header(self) -> ServiceHeaderComponent:
        header_ = self._soup.select_one("header")
        assert header_
        return ServiceHeaderComponent(header_)

    @property
    def authority(self) -> str | None:
        heading = self._soup.select_one("main h1")
        return heading.string if heading else None

    @property
    def schemes(self) -> SchemesTableComponent | None:
        table = self._soup.select_one("main table")
        return SchemesTableComponent(table) if table else None

    @property
    def is_no_schemes_message_visible(self) -> bool:
        paragraph = self._soup.select_one("main p")
        return paragraph.string == "There are no schemes for your authority to update." if paragraph else False


class ServiceHeaderComponent:
    def __init__(self, tag: Tag):
        home = tag.select_one("a.one-login-header__link")
        profile = tag.select_one("a.one-login-header__nav__link")
        sign_out = tag.select_one("a:-soup-contains('Sign out')")
        self.home_url = home["href"] if home else None
        self.profile_url = profile["href"] if profile else None
        self.sign_out_url = sign_out["href"] if sign_out else None


class SchemesTableComponent:
    def __init__(self, tag: Tag):
        self._rows = tag.select("tbody tr")

    def __iter__(self) -> Iterator[dict[str, str | None]]:
        return iter([SchemeRowComponent(row).to_dict() for row in self._rows])


class SchemeRowComponent:
    def __init__(self, tag: Tag):
        cells = tag.select("td")
        self.reference = cells[0].string
        self.name = cells[1].string

    def to_dict(self) -> dict[str, str | None]:
        return {"reference": self.reference, "name": self.name}
