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

    def __iter__(self) -> Iterator[SchemeRowComponent]:
        return iter([SchemeRowComponent(row) for row in self._rows])

    def __getitem__(self, reference: str) -> SchemeRowComponent:
        return next((scheme for scheme in self if scheme.reference == reference))

    def to_dicts(self) -> list[dict[str, str | None]]:
        return [scheme.to_dict() for scheme in self]


class SchemeRowComponent:
    def __init__(self, tag: Tag):
        cells = tag.select("td")
        reference = cells[0]
        self.reference = reference.string
        reference_link = reference.select_one("a")
        self.reference_url = reference_link.get("href") if reference_link else None
        self.name = cells[1].string

    def to_dict(self) -> dict[str, str | None]:
        return {"reference": self.reference, "name": self.name}


class SchemePage:
    def __init__(self, client: FlaskClient):
        self._client = client
        self._soup = BeautifulSoup()

    def open(self, id_: int) -> SchemePage:
        response = self._client.get(f"/schemes/{id_}")
        self._soup = BeautifulSoup(response.text, "html.parser")
        return self

    @property
    def reference_and_name(self) -> str | None:
        heading = self._soup.select_one("main h1")
        return heading.string if heading else None

    @property
    def overview(self) -> SchemeOverviewComponent:
        panel = self._soup.select_one("#overview")
        assert panel
        return SchemeOverviewComponent(panel)

    @property
    def funding(self) -> SchemeFundingComponent:
        panel = self._soup.select_one("#funding")
        assert panel
        return SchemeFundingComponent(panel)


class SchemeOverviewComponent:
    def __init__(self, tag: Tag):
        scheme_type_tag = tag.select("main dd")[0]
        self.scheme_type = scheme_type_tag.string.strip() if scheme_type_tag.string else None
        funding_programme_tag = tag.select("main dd")[1]
        self.funding_programme = funding_programme_tag.string.strip() if funding_programme_tag.string else None
        current_milestone_tag = tag.select("main dd")[2]
        self.current_milestone = current_milestone_tag.string.strip() if current_milestone_tag.string else None


class SchemeFundingComponent:
    def __init__(self, tag: Tag):
        funding_allocation_tag = tag.select("main dd")[0]
        self.funding_allocation = funding_allocation_tag.string.strip() if funding_allocation_tag.string else None
        spend_to_date_tag = tag.select("main dd")[1]
        self.spend_to_date = spend_to_date_tag.string.strip() if spend_to_date_tag.string else None
