from __future__ import annotations

from typing import Iterator

from bs4 import BeautifulSoup, Tag
from flask.testing import FlaskClient
from werkzeug.test import TestResponse


class PageObject:
    def __init__(self, response: TestResponse):
        self._response = response
        self._soup = BeautifulSoup(response.text, "html.parser")


class StartPage(PageObject):
    @classmethod
    def open(cls, client: FlaskClient) -> StartPage:
        response = client.get("/")
        return cls(response)

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
    def __init__(self, header: Tag):
        home = header.select_one("a.govuk-header__link")
        self.home_url = home["href"] if home else None


class ForbiddenPage(PageObject):
    @property
    def is_visible(self) -> bool:
        heading = self._soup.select_one("main h1")
        return heading.string == "Forbidden" if heading else False

    @property
    def is_forbidden(self) -> bool:
        return self._response.status_code == 403


class SchemesPage(PageObject):
    @classmethod
    def open(cls, client: FlaskClient) -> SchemesPage:
        response = client.get("/schemes")
        return cls(response)

    @property
    def header(self) -> ServiceHeaderComponent:
        header_ = self._soup.select_one("header")
        assert header_
        return ServiceHeaderComponent(header_)

    @property
    def authority(self) -> str | None:
        caption = self._soup.select_one("main h1 .govuk-caption-xl")
        return caption.string if caption else None

    @property
    def schemes(self) -> SchemesTableComponent | None:
        table = self._soup.select_one("main table")
        return SchemesTableComponent(table) if table else None

    @property
    def is_no_schemes_message_visible(self) -> bool:
        paragraph = self._soup.select_one("main p")
        return paragraph.string == "There are no schemes for your authority to update." if paragraph else False


class ServiceHeaderComponent:
    def __init__(self, header: Tag):
        home = header.select_one("a.one-login-header__link")
        profile = header.select_one("a.one-login-header__nav__link")
        sign_out = header.select_one("a:-soup-contains('Sign out')")
        self.home_url = home["href"] if home else None
        self.profile_url = profile["href"] if profile else None
        self.sign_out_url = sign_out["href"] if sign_out else None


class SchemesTableComponent:
    def __init__(self, table: Tag):
        self._rows = table.select("tbody tr")

    def __iter__(self) -> Iterator[SchemeRowComponent]:
        return iter([SchemeRowComponent(row) for row in self._rows])

    def __getitem__(self, reference: str) -> SchemeRowComponent:
        return next((scheme for scheme in self if scheme.reference == reference))

    def to_dicts(self) -> list[dict[str, str | None]]:
        return [scheme.to_dict() for scheme in self]


class SchemeRowComponent:
    def __init__(self, row: Tag):
        cells = row.select("td")
        reference = cells[0]
        self.reference = reference.string
        reference_link = reference.select_one("a")
        self.reference_url = reference_link.get("href") if reference_link else None
        self.funding_programme = cells[1].string or ""
        self.name = cells[2].string

    def to_dict(self) -> dict[str, str | None]:
        return {"reference": self.reference, "funding_programme": self.funding_programme, "name": self.name}


class SchemePage(PageObject):
    @classmethod
    def open(cls, client: FlaskClient, id_: int) -> SchemePage:
        response = client.get(f"/schemes/{id_}")
        return cls(response)

    @classmethod
    def open_when_unauthorized(cls, client: FlaskClient, id_: int) -> ForbiddenPage:
        response = client.get(f"/schemes/{id_}")
        return ForbiddenPage(response)

    @property
    def back_url(self) -> str | list[str] | None:
        back = self._soup.select_one("a.govuk-back-link")
        return back["href"] if back else None

    @property
    def authority(self) -> str | None:
        caption = self._soup.select_one("main h1 .govuk-caption-xl")
        return caption.string if caption else None

    @property
    def name(self) -> str | None:
        heading = self._soup.select_one("main h1 span:nth-child(2)")
        return heading.string if heading else None

    @property
    def overview(self) -> SchemeOverviewComponent:
        title = self._soup.select_one("main h2:-soup-contains('Overview')")
        assert title
        return SchemeOverviewComponent(title)

    @property
    def funding(self) -> SchemeFundingComponent:
        title = self._soup.select_one("main h2:-soup-contains('Funding')")
        assert title
        return SchemeFundingComponent(title)

    @property
    def milestones(self) -> SchemeMilestonesComponent:
        title = self._soup.select_one("main h2:-soup-contains('Milestones')")
        assert title
        return SchemeMilestonesComponent(title)

    @property
    def outputs(self) -> SchemeOutputsComponent:
        title = self._soup.select_one("main h2:-soup-contains('Outputs')")
        assert title
        return SchemeOutputsComponent(title)


class SummaryCardComponent:
    def __init__(self, title: Tag):
        card = title.find_parent("div", class_="govuk-summary-card")
        assert card
        self._card = card

    def _get_definition(self, term_text: str) -> list[Tag]:
        return self._card.select(f"dt:-soup-contains('{term_text}') ~ dd")


class SchemeOverviewComponent(SummaryCardComponent):
    def __init__(self, title: Tag):
        super().__init__(title)
        self.reference = (self._get_definition("Reference")[0].string or "").strip()
        self.scheme_type = (self._get_definition("Scheme type")[0].string or "").strip()
        self.funding_programme = (self._get_definition("Funding programme")[0].string or "").strip()
        self.current_milestone = (self._get_definition("Current milestone")[0].string or "").strip()


class SchemeFundingComponent(SummaryCardComponent):
    def __init__(self, title: Tag):
        super().__init__(title)
        self.funding_allocation = (self._get_definition("Funding allocation")[0].string or "").strip()
        self.change_control_adjustment = (self._get_definition("Change control adjustment")[0].string or "").strip()
        self.spend_to_date = (self._get_definition("Spend to date")[0].string or "").strip()
        self.allocation_still_to_spend = (self._get_definition("Allocation still to spend")[0].string or "").strip()


class SchemeMilestonesComponent:
    def __init__(self, title: Tag):
        card = title.find_parent("div", class_="govuk-summary-card")
        assert card
        table = card.select_one("table")
        assert table
        self.milestones = SchemeMilestonesTableComponent(table)


class SchemeMilestonesTableComponent:
    def __init__(self, table: Tag):
        self._rows = table.select("tbody tr")

    def __iter__(self) -> Iterator[SchemeMilestoneRowComponent]:
        return iter([SchemeMilestoneRowComponent(row) for row in self._rows])

    def to_dicts(self) -> list[dict[str, str | None]]:
        return [milestone.to_dict() for milestone in self]


class SchemeMilestoneRowComponent:
    def __init__(self, row: Tag):
        header = row.select_one("th")
        self.milestone = header.string if header else None
        cells = row.select("td")
        self.planned = cells[0].string
        self.actual = cells[1].string

    def to_dict(self) -> dict[str, str | None]:
        return {"milestone": self.milestone, "planned": self.planned, "actual": self.actual}


class SchemeOutputsComponent:
    def __init__(self, title: Tag):
        card = title.find_parent("div", class_="govuk-summary-card")
        assert card
        table = card.select_one("table")
        self.outputs = SchemeOutputsTableComponent(table) if table else None
        paragraph = card.select_one("p")
        self.is_no_outputs_message_visible = (
            paragraph.string == "There are no outputs for this scheme." if paragraph else None
        )


class SchemeOutputsTableComponent:
    def __init__(self, table: Tag):
        self._rows = table.select("tbody tr")

    def __iter__(self) -> Iterator[SchemeOutputRowComponent]:
        return iter([SchemeOutputRowComponent(row) for row in self._rows])

    def to_dicts(self) -> list[dict[str, str | None]]:
        return [output.to_dict() for output in self]


class SchemeOutputRowComponent:
    def __init__(self, row: Tag):
        cells = row.select("td")
        self.infrastructure = cells[0].string
        self.measurement = cells[1].string
        self.planned = cells[2].string

    def to_dict(self) -> dict[str, str | None]:
        return {
            "infrastructure": self.infrastructure,
            "measurement": self.measurement,
            "planned": self.planned,
        }
