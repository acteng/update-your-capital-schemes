from __future__ import annotations

from typing import Iterator

from bs4 import BeautifulSoup, Tag
from flask.testing import FlaskClient
from werkzeug.test import TestResponse


class PageObject:
    def __init__(self, response: TestResponse):
        self._response = response
        self._soup = BeautifulSoup(response.text, "html.parser")

    @property
    def title(self) -> str | None:
        title = self._soup.select_one("title")
        return title.text if title else None


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
        return (SchemeRowComponent(row) for row in self._rows)

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
        spend_to_date_link = self._get_definition("Spend to date")[1].select_one("a")
        self.change_spend_to_date_url = spend_to_date_link.get("href") if spend_to_date_link else None
        self.allocation_still_to_spend = (self._get_definition("Allocation still to spend")[0].string or "").strip()


class SchemeMilestonesComponent:
    def __init__(self, title: Tag):
        title_wrapper = title.find_parent("div", class_="govuk-summary-card__title-wrapper")
        assert title_wrapper
        change_milestones = title_wrapper.select_one("a:-soup-contains('Change')")
        self.change_milestones_url = change_milestones["href"] if change_milestones else None
        card = title_wrapper.find_parent("div", class_="govuk-summary-card")
        assert card
        table = card.select_one("table")
        assert table
        self.milestones = SchemeMilestonesTableComponent(table)


class SchemeMilestonesTableComponent:
    def __init__(self, table: Tag):
        self._rows = table.select("tbody tr")

    def __iter__(self) -> Iterator[SchemeMilestoneRowComponent]:
        return (SchemeMilestoneRowComponent(row) for row in self._rows)

    def to_dicts(self) -> list[dict[str, str | None]]:
        return [milestone.to_dict() for milestone in self]


class SchemeMilestoneRowComponent:
    def __init__(self, row: Tag):
        header = row.select_one("th")
        self.milestone = header.string if header else None
        cells = row.select("td")
        self.planned = cells[0].string or ""
        self.actual = cells[1].string or ""

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
        return (SchemeOutputRowComponent(row) for row in self._rows)

    def to_dicts(self) -> list[dict[str, str | None]]:
        return [output.to_dict() for output in self]


class SchemeOutputRowComponent:
    def __init__(self, row: Tag):
        cells = row.select("td")
        self.infrastructure = cells[0].string
        self.measurement = cells[1].string
        self.planned = cells[2].string or ""

    def to_dict(self) -> dict[str, str | None]:
        return {
            "infrastructure": self.infrastructure,
            "measurement": self.measurement,
            "planned": self.planned,
        }


class ChangeSpendToDatePage(PageObject):
    def __init__(self, response: TestResponse):
        super().__init__(response)
        back = self._soup.select_one("a.govuk-back-link")
        self.back_url = back["href"] if back else None
        alert = self._soup.select_one(".govuk-error-summary div[role='alert']")
        self.errors = ErrorSummaryComponent(alert) if alert else None
        notification_banner_tag = self._soup.select_one(".govuk-notification-banner")
        self.notification_banner = (
            NotificationBannerComponent(notification_banner_tag) if notification_banner_tag else None
        )
        paragraph = self._soup.select_one("main p")
        self.funding_summary = (paragraph.string or "").strip() if paragraph else None
        form_tag = self._soup.select_one("form")
        assert form_tag
        self.form = ChangeSpendToDateFormComponent(form_tag)

    @classmethod
    def open(cls, client: FlaskClient, id_: int) -> ChangeSpendToDatePage:
        response = client.get(f"/schemes/{id_}/spend-to-date")
        return cls(response)

    @classmethod
    def open_when_unauthorized(cls, client: FlaskClient, id_: int) -> ForbiddenPage:
        response = client.get(f"/schemes/{id_}/spend-to-date")
        return ForbiddenPage(response)

    @property
    def is_visible(self) -> bool:
        heading = self._soup.select_one("main h1")
        return heading.string == "Change spend to date" if heading else False


class ChangeMilestoneDatesPage(PageObject):
    def __init__(self, response: TestResponse):
        super().__init__(response)
        back = self._soup.select_one("a.govuk-back-link")
        self.back_url = back["href"] if back else None
        alert = self._soup.select_one(".govuk-error-summary div[role='alert']")
        self.errors = ErrorSummaryComponent(alert) if alert else None
        notification_banner_tag = self._soup.select_one(".govuk-notification-banner")
        self.notification_banner = (
            NotificationBannerComponent(notification_banner_tag) if notification_banner_tag else None
        )
        form_tag = self._soup.select_one("form")
        assert form_tag
        self.form = ChangeMilestoneDatesFormComponent(form_tag)

    @classmethod
    def open(cls, client: FlaskClient, id_: int) -> ChangeMilestoneDatesPage:
        response = client.get(f"/schemes/{id_}/milestones")
        return cls(response)

    @property
    def is_visible(self) -> bool:
        heading = self._soup.select_one("main h1")
        return heading.string == "Change milestone dates" if heading else False


class ErrorSummaryComponent:
    def __init__(self, alert: Tag):
        self._alert = alert

    def __iter__(self) -> Iterator[str]:
        return (listitem.text.strip() for listitem in self._alert.select("li"))


class NotificationBannerComponent:
    def __init__(self, banner: Tag):
        heading_tag = banner.select_one("p")
        self.heading = heading_tag.string if heading_tag else None


class ChangeSpendToDateFormComponent:
    def __init__(self, form: Tag):
        self._form = form
        self.confirm_url = form.get("action")
        amount_input = form.select_one("input[name='amount']")
        assert amount_input
        self.amount = TextComponent(amount_input)
        cancel = self._form.select_one("a")
        self.cancel_url = cancel["href"] if cancel else None


class ChangeMilestoneDatesFormComponent:
    def __init__(self, form: Tag):
        self.confirm_url = form.get("action")
        construction_started_tag = form.select_one("h2:-soup-contains('Construction started')")
        assert construction_started_tag
        self.construction_started = ChangeMilestoneDatesFormRowComponent(construction_started_tag)


class ChangeMilestoneDatesFormRowComponent:
    def __init__(self, heading: Tag):
        grid_row = heading.find_next_sibling("div", class_="govuk-grid-row")
        assert isinstance(grid_row, Tag)
        planned_tag = grid_row.select_one("fieldset:has(legend:-soup-contains('Planned date'))")
        assert planned_tag
        self.planned = DateComponent(planned_tag)
        actual_tag = grid_row.select_one("fieldset:has(legend:-soup-contains('Actual date'))")
        assert actual_tag
        self.actual = DateComponent(actual_tag)

    def __getitem__(self, item: str) -> DateComponent:
        match item:
            case "planned":
                return self.planned
            case "actual":
                return self.actual
            case _:
                raise ValueError(f"Unknown item: {item}")


class DateComponent:
    def __init__(self, fieldset: Tag):
        inputs = fieldset.select("input")
        self.day = TextComponent(inputs[0])
        self.month = TextComponent(inputs[1])
        self.year = TextComponent(inputs[2])
        self.value = f"{self.day.value} {self.month.value} {self.year.value}"
        self.is_errored = self.day.is_errored and self.month.is_errored and self.year.is_errored
        error_message = fieldset.select_one(".govuk-error-message")
        self.error = error_message.text.strip() if error_message else None


class TextComponent:
    def __init__(self, input_: Tag):
        self.value = input_.get("value")
        self.is_errored = "govuk-input--error" in input_.get_attribute_list("class")
        form_group = input_.find_parent("div", class_="govuk-form-group")
        assert form_group
        error_message = form_group.select_one(".govuk-error-message")
        self.error = error_message.text.strip() if error_message else None
