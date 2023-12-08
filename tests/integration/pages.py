from __future__ import annotations

from typing import Iterator

from bs4 import BeautifulSoup, Tag
from flask.testing import FlaskClient
from werkzeug.test import TestResponse


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


class ForbiddenPage:
    def __init__(self, response: TestResponse):
        self._response = response
        self._soup = BeautifulSoup(self._response.text, "html.parser")

    @property
    def is_visible(self) -> bool:
        heading = self._soup.select_one("main h1")
        return heading.string == "Forbidden" if heading else False

    @property
    def is_forbidden(self) -> bool:
        return self._response.status_code == 403


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
        self.funding_programme = cells[1].string
        self.name = cells[2].string

    def to_dict(self) -> dict[str, str | None]:
        return {"reference": self.reference, "funding_programme": self.funding_programme, "name": self.name}


class SchemePage:
    def __init__(self, client: FlaskClient):
        self._client = client
        self._soup = BeautifulSoup()

    def open(self, id_: int) -> SchemePage:
        response = self._client.get(f"/schemes/{id_}")
        self._soup = BeautifulSoup(response.text, "html.parser")
        return self

    def open_when_unauthorized(self, id_: int) -> ForbiddenPage:
        response = self._client.get(f"/schemes/{id_}")
        return ForbiddenPage(response)

    @property
    def back_url(self) -> str | list[str] | None:
        back = self._soup.select_one("a.govuk-back-link")
        return back["href"] if back else None

    @property
    def name(self) -> str | None:
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

    @property
    def milestones(self) -> SchemeMilestonesComponent:
        panel = self._soup.select_one("#milestones")
        assert panel
        return SchemeMilestonesComponent(panel)

    @property
    def outputs(self) -> SchemeOutputsComponent:
        panel = self._soup.select_one("#outputs")
        assert panel
        return SchemeOutputsComponent(panel)


class SchemeOverviewComponent:
    def __init__(self, tag: Tag):
        self.reference = (tag.select("main dd")[0].string or "").strip()
        self.scheme_type = (tag.select("main dd")[1].string or "").strip()
        self.funding_programme = (tag.select("main dd")[2].string or "").strip()
        self.current_milestone = (tag.select("main dd")[3].string or "").strip()


class SchemeFundingComponent:
    def __init__(self, tag: Tag):
        self.funding_allocation = (tag.select("main dd")[0].string or "").strip()
        self.spend_to_date = (tag.select("main dd")[1].string or "").strip()
        self.change_control_adjustment = (tag.select("main dd")[2].string or "").strip()
        self.allocation_still_to_spend = (tag.select("main dd")[3].string or "").strip()


class SchemeMilestonesComponent:
    def __init__(self, tag: Tag):
        milestones_table = tag.select_one("table")
        assert milestones_table
        self.milestones = SchemeMilestonesTableComponent(milestones_table)


class SchemeMilestonesTableComponent:
    def __init__(self, tag: Tag):
        self._rows = tag.select("tbody tr")

    def __iter__(self) -> Iterator[SchemeMilestoneRowComponent]:
        return iter([SchemeMilestoneRowComponent(row) for row in self._rows])

    def to_dicts(self) -> list[dict[str, str | None]]:
        return [milestone.to_dict() for milestone in self]


class SchemeMilestoneRowComponent:
    def __init__(self, tag: Tag):
        milestone_tag = tag.select_one("th")
        self.milestone = milestone_tag.string if milestone_tag else None
        cells = tag.select("td")
        self.planned = cells[0].string
        self.actual = cells[1].string

    def to_dict(self) -> dict[str, str | None]:
        return {"milestone": self.milestone, "planned": self.planned, "actual": self.actual}


class SchemeOutputsComponent:
    def __init__(self, tag: Tag):
        outputs_table = tag.select_one("table")
        self.outputs = SchemeOutputsTableComponent(outputs_table) if outputs_table else None
        paragraph = tag.select_one("p")
        self.is_no_outputs_message_visible = (
            paragraph.string == "There are no outputs for this scheme." if paragraph else None
        )


class SchemeOutputsTableComponent:
    def __init__(self, tag: Tag):
        self._rows = tag.select("tbody tr")

    def __iter__(self) -> Iterator[SchemeOutputRowComponent]:
        return iter([SchemeOutputRowComponent(row) for row in self._rows])

    def to_dicts(self) -> list[dict[str, str | None]]:
        return [output.to_dict() for output in self]


class SchemeOutputRowComponent:
    def __init__(self, tag: Tag):
        cells = tag.select("td")
        self.infrastructure = cells[0].string
        self.measurement = cells[1].string
        self.planned = cells[2].string

    def to_dict(self) -> dict[str, str | None]:
        return {
            "infrastructure": self.infrastructure,
            "measurement": self.measurement,
            "planned": self.planned,
        }
