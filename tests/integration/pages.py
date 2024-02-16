from __future__ import annotations

from typing import Iterator

from bs4 import BeautifulSoup, ResultSet, Tag
from flask.testing import FlaskClient
from werkzeug.test import TestResponse


class PageObject:
    def __init__(self, response: TestResponse):
        self._response = response
        self._soup = BeautifulSoup(response.text, "html.parser")
        self.title = one(self._soup.select("title")).text


class StartPage(PageObject):
    def __init__(self, response: TestResponse):
        super().__init__(response)
        self.header = HeaderComponent(one(self._soup.select("header")))
        heading = self._soup.select_one("main h1")
        self.is_visible = heading.string == "Update your capital schemes" if heading else False

    @classmethod
    def open(cls, client: FlaskClient) -> StartPage:
        response = client.get("/")
        return cls(response)


class HeaderComponent:
    def __init__(self, header: Tag):
        self.home_url = one(header.select("a.govuk-header__link"))["href"]


class ForbiddenPage(PageObject):
    def __init__(self, response: TestResponse):
        super().__init__(response)
        heading = self._soup.select_one("main h1")
        self.is_visible = heading.string == "Forbidden" if heading else False
        self.is_forbidden = response.status_code == 403


class SchemesPage(PageObject):
    def __init__(self, response: TestResponse):
        super().__init__(response)
        self.header = ServiceHeaderComponent(one(self._soup.select("header")))
        notification_banner_tag = self._soup.select_one(".govuk-notification-banner")
        self.notification_banner = (
            NotificationBannerComponent(notification_banner_tag) if notification_banner_tag else None
        )
        self.authority = one(self._soup.select("main h1 .govuk-caption-xl")).string
        table = self._soup.select_one("main table")
        self.schemes = SchemesTableComponent(table) if table else None
        paragraph = self._soup.select_one("main h1 ~ p")
        self.is_no_schemes_message_visible = (
            paragraph.string == "There are no schemes for your authority to update." if paragraph else False
        )

    @classmethod
    def open(cls, client: FlaskClient) -> SchemesPage:
        response = client.get("/schemes")
        return cls(response)


class ServiceHeaderComponent:
    def __init__(self, header: Tag):
        self.home_url = one(header.select("a.one-login-header__link"))["href"]
        self.profile_url = one(header.select("a:-soup-contains('GOV.UK One Login')"))["href"]
        self.sign_out_url = one(header.select("a:-soup-contains('Sign out')"))["href"]


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
        self.reference_url = one(reference.select("a")).get("href")
        self.funding_programme = cells[1].string or ""
        self.name = cells[2].string

    def to_dict(self) -> dict[str, str | None]:
        return {"reference": self.reference, "funding_programme": self.funding_programme, "name": self.name}


class SchemePage(PageObject):
    def __init__(self, response: TestResponse):
        super().__init__(response)
        self.back_url = one(self._soup.select("a.govuk-back-link"))["href"]
        self.authority = one(self._soup.select("main h1 .govuk-caption-xl")).string
        self.name = one(self._soup.select("main h1 span:nth-child(2)")).string
        self.overview = SchemeOverviewComponent(one(self._soup.select("main h2:-soup-contains('Overview')")))
        self.funding = SchemeFundingComponent(one(self._soup.select("main h2:-soup-contains('Funding')")))
        self.milestones = SchemeMilestonesComponent(one(self._soup.select("main h2:-soup-contains('Milestones')")))
        self.outputs = SchemeOutputsComponent(one(self._soup.select("main h2:-soup-contains('Outputs')")))

    @classmethod
    def open(cls, client: FlaskClient, id_: int) -> SchemePage:
        response = client.get(f"/schemes/{id_}")
        return cls(response)

    @classmethod
    def open_when_unauthorized(cls, client: FlaskClient, id_: int) -> ForbiddenPage:
        response = client.get(f"/schemes/{id_}")
        return ForbiddenPage(response)


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
        self.change_spend_to_date_url = one(self._get_definition("Spend to date")[1].select("a")).get("href")
        self.allocation_still_to_spend = (self._get_definition("Allocation still to spend")[0].string or "").strip()


class SchemeMilestonesComponent:
    def __init__(self, title: Tag):
        title_wrapper = title.find_parent("div", class_="govuk-summary-card__title-wrapper")
        assert title_wrapper
        self.change_milestones_url = one(title_wrapper.select("a:-soup-contains('Change')"))["href"]
        card = title_wrapper.find_parent("div", class_="govuk-summary-card")
        assert card
        self.milestones = SchemeMilestonesTableComponent(one(card.select("table")))


class SchemeMilestonesTableComponent:
    def __init__(self, table: Tag):
        self._rows = table.select("tbody tr")

    def __iter__(self) -> Iterator[SchemeMilestoneRowComponent]:
        return (SchemeMilestoneRowComponent(row) for row in self._rows)

    def to_dicts(self) -> list[dict[str, str | None]]:
        return [milestone.to_dict() for milestone in self]


class SchemeMilestoneRowComponent:
    def __init__(self, row: Tag):
        self.milestone = one(row.select("th")).string
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
        heading = self._soup.select_one("main h1")
        self.is_visible = heading.string == "Change spend to date" if heading else False
        self.back_url = one(self._soup.select("a.govuk-back-link"))["href"]
        alert = self._soup.select_one(".govuk-error-summary div[role='alert']")
        self.errors = ErrorSummaryComponent(alert) if alert else None
        notification_banner_tag = self._soup.select_one(".govuk-notification-banner")
        self.notification_banner = (
            NotificationBannerComponent(notification_banner_tag) if notification_banner_tag else None
        )
        self.funding_summary = (one(self._soup.select("main h1 ~ p")).string or "").strip()
        self.form = ChangeSpendToDateFormComponent(one(self._soup.select("form")))

    @classmethod
    def open(cls, client: FlaskClient, id_: int) -> ChangeSpendToDatePage:
        response = client.get(f"/schemes/{id_}/spend-to-date")
        return cls(response)

    @classmethod
    def open_when_unauthorized(cls, client: FlaskClient, id_: int) -> ForbiddenPage:
        response = client.get(f"/schemes/{id_}/spend-to-date")
        return ForbiddenPage(response)


class ChangeMilestoneDatesPage(PageObject):
    def __init__(self, response: TestResponse):
        super().__init__(response)
        heading = self._soup.select_one("main h1")
        self.is_visible = heading.string == "Change milestone dates" if heading else False
        self.back_url = one(self._soup.select("a.govuk-back-link"))["href"]
        alert = self._soup.select_one(".govuk-error-summary div[role='alert']")
        self.errors = ErrorSummaryComponent(alert) if alert else None
        notification_banner_tag = self._soup.select_one(".govuk-notification-banner")
        self.notification_banner = (
            NotificationBannerComponent(notification_banner_tag) if notification_banner_tag else None
        )
        self.form = ChangeMilestoneDatesFormComponent(one(self._soup.select("form")))

    @classmethod
    def open(cls, client: FlaskClient, id_: int) -> ChangeMilestoneDatesPage:
        response = client.get(f"/schemes/{id_}/milestones")
        return cls(response)

    @classmethod
    def open_when_unauthorized(cls, client: FlaskClient, id_: int) -> ForbiddenPage:
        response = client.get(f"/schemes/{id_}/milestones")
        return ForbiddenPage(response)


class ErrorSummaryComponent:
    def __init__(self, alert: Tag):
        self._alert = alert

    def __iter__(self) -> Iterator[str]:
        return (listitem.text.strip() for listitem in self._alert.select("li"))


class NotificationBannerComponent:
    def __init__(self, banner: Tag):
        self.heading = one(banner.select("p")).string


class ChangeSpendToDateFormComponent:
    def __init__(self, form: Tag):
        self._form = form
        self.confirm_url = form["action"]
        self.amount = TextComponent(one(form.select("input[name='amount']")))
        self.cancel_url = one(self._form.select("a"))["href"]


class ChangeMilestoneDatesFormComponent:
    def __init__(self, form: Tag):
        self.confirm_url = form["action"]
        self.feasibility_design_completed = ChangeMilestoneDatesFormRowComponent(
            one(form.select("h2:-soup-contains('Feasibility design completed')"))
        )
        self.preliminary_design_completed = ChangeMilestoneDatesFormRowComponent(
            one(form.select("h2:-soup-contains('Preliminary design completed')"))
        )
        self.detailed_design_completed = ChangeMilestoneDatesFormRowComponent(
            one(form.select("h2:-soup-contains('Detailed design completed')"))
        )
        self.construction_started = ChangeMilestoneDatesFormRowComponent(
            one(form.select("h2:-soup-contains('Construction started')"))
        )
        self.construction_completed = ChangeMilestoneDatesFormRowComponent(
            one(form.select("h2:-soup-contains('Construction completed')"))
        )
        self.cancel_url = one(form.select("a"))["href"]


class ChangeMilestoneDatesFormRowComponent:
    def __init__(self, heading: Tag):
        grid_row = heading.find_next_sibling("div", class_="govuk-grid-row")
        assert isinstance(grid_row, Tag)
        self.planned = DateComponent(one(grid_row.select("fieldset:has(legend:-soup-contains('Planned date'))")))
        self.actual = DateComponent(one(grid_row.select("fieldset:has(legend:-soup-contains('Actual date'))")))


class DateComponent:
    def __init__(self, fieldset: Tag):
        inputs = fieldset.select("input")
        self.day = TextComponent(inputs[0])
        self.month = TextComponent(inputs[1])
        self.year = TextComponent(inputs[2])
        self.name = self.day.name
        self.value = f"{self.day.value} {self.month.value} {self.year.value}"
        self.is_errored = self.day.is_errored and self.month.is_errored and self.year.is_errored
        error_message = fieldset.select_one(".govuk-error-message")
        self.error = error_message.text.strip() if error_message else None


class TextComponent:
    def __init__(self, input_: Tag):
        self.name = input_["name"]
        self.value = input_.get("value")
        self.is_errored = "govuk-input--error" in input_.get_attribute_list("class")
        form_group = input_.find_parent("div", class_="govuk-form-group")
        assert form_group
        error_message = form_group.select_one(".govuk-error-message")
        self.error = error_message.text.strip() if error_message else None


def one(tags: ResultSet[Tag]) -> Tag:
    (tag,) = tags
    return tag
