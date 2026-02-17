import re
from re import Pattern
from typing import Iterator, Self

from bs4 import BeautifulSoup, ResultSet, Tag
from flask.testing import FlaskClient
from werkzeug.test import TestResponse

from tests.integration.conftest import AsyncFlaskClient


class PageMetadata:
    def __init__(self, head: Tag):
        self.image_url = one(head.select("meta[property='og:image']"))["content"]


class PageObject:
    def __init__(self, response: TestResponse):
        self._response = response
        self._soup = BeautifulSoup(response.text, "html.parser")

    @property
    def title(self) -> str:
        return one(self._soup.select("head > title")).get_text()

    @property
    def metadata(self) -> PageMetadata:
        return PageMetadata(one(self._soup.select("head")))


class HeaderComponent:
    def __init__(self, header: Tag):
        self.home_url = one(header.select("a.govuk-header__homepage-link"))["href"]


class FooterComponent:
    def __init__(self, footer: Tag):
        list_items = footer.select(".govuk-footer__inline-list a")
        self.privacy_url = list_items[0]["href"]
        self.accessibility_url = list_items[1]["href"]
        self.cookies_url = list_items[2]["href"]


class StartPage(PageObject):
    def __init__(self, response: TestResponse):
        super().__init__(response)
        heading = self._soup.select_one("main h1")
        self.is_visible = heading.string == "Update your capital schemes" if heading else False

    @property
    def header(self) -> HeaderComponent:
        return HeaderComponent(one(self._soup.select(".govuk-header")))

    @property
    def footer(self) -> FooterComponent:
        return FooterComponent(one(self._soup.select(".govuk-footer")))

    @classmethod
    def open(cls, client: FlaskClient) -> Self:
        response = client.get("/")
        return cls(response)


class PrivacyPage(PageObject):
    def __init__(self, response: TestResponse):
        super().__init__(response)
        heading = self._soup.select_one("main h1")
        self.is_visible = heading.string == "Privacy notice" if heading else False

    @classmethod
    def open(cls, client: FlaskClient) -> Self:
        response = client.get("/privacy")
        return cls(response)


class CookiesPage(PageObject):
    def __init__(self, response: TestResponse):
        super().__init__(response)
        heading = self._soup.select_one("main h1")
        self.is_visible = heading.string == "Cookies" if heading else False

    @classmethod
    def open(cls, client: FlaskClient) -> Self:
        response = client.get("/cookies")
        return cls(response)


class AccessibilityPage(PageObject):
    def __init__(self, response: TestResponse):
        super().__init__(response)
        heading = self._soup.select_one("main h1")
        self.is_visible = heading.string == "Accessibility statement" if heading else False

    @classmethod
    def open(cls, client: FlaskClient) -> Self:
        response = client.get("/accessibility")
        return cls(response)


class BadRequestPage(PageObject):
    def __init__(self, response: TestResponse):
        super().__init__(response)
        heading = self._soup.select_one("main h1")
        self.is_visible = heading.string == "Bad request" if heading else False
        self.is_bad_request = response.status_code == 400


class ForbiddenPage(PageObject):
    def __init__(self, response: TestResponse):
        super().__init__(response)
        heading = self._soup.select_one("main h1")
        self.is_visible = heading.string == "Forbidden" if heading else False
        self.is_forbidden = response.status_code == 403

    @classmethod
    def open(cls, client: FlaskClient) -> Self:
        response = client.get("/auth/forbidden")
        return cls(response)


class NotFoundPage(PageObject):
    def __init__(self, response: TestResponse):
        super().__init__(response)
        heading = self._soup.select_one("main h1")
        self.is_visible = heading.string == "Page not found" if heading else False
        self.is_not_found = response.status_code == 404


class ServiceHeaderComponent:
    def __init__(self, header: Tag):
        self.home_url = one(header.select("a.rebranded-one-login-header__link"))["href"]
        self.profile_url = one(header.select("a:-soup-contains('GOV.UK One Login')"))["href"]
        self.sign_out_url = one(header.select("a:-soup-contains('Sign out')"))["href"]


class SchemesPage(PageObject):
    def __init__(self, response: TestResponse):
        super().__init__(response)
        self.success_notification = NotificationBannerComponent.for_success(self._soup)
        self.important_notification = NotificationBannerComponent.for_important(self._soup)
        heading_tag = self._soup.select_one("main h1")
        self.heading = HeadingComponent(heading_tag) if heading_tag else None
        self.is_visible = self.heading.text == "Your schemes" if self.heading else False
        table = self._soup.select_one("main table")
        self.schemes = SchemesTableComponent(table) if table else None
        paragraph = self._soup.select_one("main h1 ~ p")
        self.is_no_schemes_message_visible = (
            paragraph.string == "There are no schemes for your authority to update." if paragraph else False
        )

    @property
    def header(self) -> ServiceHeaderComponent:
        return ServiceHeaderComponent(one(self._soup.select("header")))

    @classmethod
    async def open(cls, client: AsyncFlaskClient) -> Self:
        response = await client.get("/schemes")
        return cls(response)


class HeadingComponent:
    def __init__(self, heading: Tag):
        self.caption = one(heading.select(".govuk-caption-xl, .govuk-caption-l")).string
        self.text = one(heading.select("span:nth-child(2)")).string


class SchemeRowComponent:
    def __init__(self, row: Tag):
        cells = row.select("td")
        reference = cells[0]
        self.reference = reference.string
        self.reference_url = one(reference.select("a")).get("href")
        self.funding_programme = cells[1].string or ""
        name_cell = cells[2]
        self.name = one(name_cell.select("span")).string
        tag = name_cell.select_one(".govuk-tag")
        self.needs_review = TagComponent(tag).text == "Needs review" if tag else False
        self.last_reviewed = cells[3].string or ""

    def to_dict(self) -> dict[str, str | bool | None]:
        return {
            "reference": self.reference,
            "funding_programme": self.funding_programme,
            "name": self.name,
            "needs_review": self.needs_review,
            "last_reviewed": self.last_reviewed,
        }


class SchemesTableComponent:
    def __init__(self, table: Tag):
        self._rows = table.select("tbody tr")

    def __iter__(self) -> Iterator[SchemeRowComponent]:
        return (SchemeRowComponent(row) for row in self._rows)

    def __getitem__(self, reference: str) -> SchemeRowComponent:
        return next((scheme for scheme in self if scheme.reference == reference))

    def to_dicts(self) -> list[dict[str, str | bool | None]]:
        return [scheme.to_dict() for scheme in self]


class TagComponent:
    def __init__(self, tag: Tag):
        self.text = (tag.string or "").strip()


class SummaryCardComponent:
    def __init__(self, title: Tag):
        card = title.find_parent("div", class_="govuk-summary-card")
        assert isinstance(card, Tag)
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
        self.spend_to_date = (self._get_definition("Spend to date")[0].string or "").strip()
        self.change_spend_to_date_url = one(self._get_definition("Spend to date")[1].select("a")).get("href")
        self.allocation_still_to_spend = (self._get_definition("Allocation still to spend")[0].string or "").strip()


class SchemeMilestonesComponent:
    def __init__(self, title: Tag):
        title_wrapper = title.find_parent("div", class_="govuk-summary-card__title-wrapper")
        assert isinstance(title_wrapper, Tag)
        self.change_milestones_url = one(title_wrapper.select("a:-soup-contains('Change')"))["href"]
        card = title_wrapper.find_parent("div", class_="govuk-summary-card")
        assert isinstance(card, Tag)
        self.milestones = SchemeMilestonesTableComponent(one(card.select("table")))


class SchemeOutputsComponent:
    def __init__(self, title: Tag):
        card = title.find_parent("div", class_="govuk-summary-card")
        assert isinstance(card, Tag)
        table = card.select_one("table")
        self.outputs = SchemeOutputsTableComponent(table) if table else None
        paragraph = card.select_one("p")
        self.is_no_outputs_message_visible = (
            paragraph.string == "There are no outputs for this scheme." if paragraph else None
        )


class SchemeReviewComponent:
    def __init__(self, heading: Tag):
        section = heading.find_parent("section")
        assert isinstance(section, Tag)
        self.last_reviewed = (one(section.select("section > p")).string or "").strip()
        self.form = SchemeReviewFormComponent(one(section.select("form")))


class SchemePage(PageObject):
    def __init__(self, response: TestResponse):
        super().__init__(response)
        alert = self._soup.select_one(".govuk-error-summary div[role='alert']")
        self.errors = ErrorSummaryComponent(alert) if alert else None
        self.important_notification = NotificationBannerComponent.for_important(self._soup)
        heading_tag = self._soup.select_one("main h1")
        self.heading = HeadingComponent(heading_tag) if heading_tag else None
        inset_text = self._soup.select_one("main .govuk-inset-text")
        self.needs_review = (
            InsetTextComponent(inset_text).has_text(
                re.compile(r"Needs review\s+Check the details before confirming that this scheme is up-to-date.")
            )
            if inset_text
            else False
        )

    @property
    def back_url(self) -> str:
        return str(one(self._soup.select("a.govuk-back-link"))["href"])

    @property
    def overview(self) -> SchemeOverviewComponent:
        return SchemeOverviewComponent(one(self._soup.select("main h2:-soup-contains('Overview')")))

    @property
    def funding(self) -> SchemeFundingComponent:
        return SchemeFundingComponent(one(self._soup.select("main h2:-soup-contains('Funding')")))

    @property
    def milestones(self) -> SchemeMilestonesComponent:
        return SchemeMilestonesComponent(one(self._soup.select("main h2:-soup-contains('Milestones')")))

    @property
    def outputs(self) -> SchemeOutputsComponent:
        return SchemeOutputsComponent(one(self._soup.select("main h2:-soup-contains('Outputs')")))

    @property
    def review(self) -> SchemeReviewComponent:
        return SchemeReviewComponent(one(self._soup.select("main h2:-soup-contains('Is this scheme up-to-date?')")))

    @classmethod
    async def open(cls, client: AsyncFlaskClient, reference: str) -> Self:
        response = await client.get(f"/schemes/{reference}")
        return cls(response)

    @classmethod
    async def open_when_unauthorized(cls, client: AsyncFlaskClient, reference: str) -> ForbiddenPage:
        response = await client.get(f"/schemes/{reference}")
        return ForbiddenPage(response)

    @classmethod
    async def open_when_not_found(cls, client: AsyncFlaskClient, reference: str) -> NotFoundPage:
        response = await client.get(f"/schemes/{reference}")
        return NotFoundPage(response)


class InsetTextComponent:
    def __init__(self, inset_text: Tag):
        self.inset_text = inset_text

    def text(self) -> str:
        return self.inset_text.get_text().strip()

    def has_text(self, pattern: Pattern[str]) -> bool:
        return pattern.match(self.text()) is not None


class SchemeMilestoneRowComponent:
    def __init__(self, row: Tag):
        self.milestone = one(row.select("th")).string
        cells = row.select("td")
        self.planned = cells[0].string or ""
        self.actual = cells[1].string or ""

    def to_dict(self) -> dict[str, str | None]:
        return {"milestone": self.milestone, "planned": self.planned, "actual": self.actual}


class SchemeMilestonesTableComponent:
    def __init__(self, table: Tag):
        self._rows = table.select("tbody tr")

    def __iter__(self) -> Iterator[SchemeMilestoneRowComponent]:
        return (SchemeMilestoneRowComponent(row) for row in self._rows)

    def to_dicts(self) -> list[dict[str, str | None]]:
        return [milestone.to_dict() for milestone in self]


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


class SchemeOutputsTableComponent:
    def __init__(self, table: Tag):
        self._rows = table.select("tbody tr")

    def __iter__(self) -> Iterator[SchemeOutputRowComponent]:
        return (SchemeOutputRowComponent(row) for row in self._rows)

    def to_dicts(self) -> list[dict[str, str | None]]:
        return [output.to_dict() for output in self]


class SchemeReviewFormComponent:
    def __init__(self, form: Tag):
        self._form = form
        self.confirm_url = form["action"]
        self.up_to_date = CheckboxComponent(one(form.select("input[name='up_to_date']")))


class ChangeSpendToDateFormComponent:
    def __init__(self, form: Tag):
        self._form = form
        self.confirm_url = form["action"]
        self.heading = HeadingComponent(one(self._form.select("h1")))
        self.funding_summary = (one(self._form.select(".govuk-hint")).string or "").strip()
        self.amount = TextComponent(one(form.select("input[name='amount']")))
        self.cancel_url = one(self._form.select("a"))["href"]


class ChangeSpendToDatePage(PageObject):
    def __init__(self, response: TestResponse):
        super().__init__(response)
        alert = self._soup.select_one(".govuk-error-summary div[role='alert']")
        self.errors = ErrorSummaryComponent(alert) if alert else None
        self.important_notification = NotificationBannerComponent.for_important(self._soup)
        heading_tag = self._soup.select_one("main h1")
        heading = HeadingComponent(heading_tag) if heading_tag else None
        self.is_visible = heading.text == "How much has been spent to date?" if heading else False

    @property
    def back_url(self) -> str:
        return str(one(self._soup.select("a.govuk-back-link"))["href"])

    @property
    def form(self) -> ChangeSpendToDateFormComponent:
        return ChangeSpendToDateFormComponent(one(self._soup.select("form")))

    @classmethod
    async def open(cls, client: AsyncFlaskClient, reference: str) -> Self:
        response = await client.get(f"/schemes/{reference}/spend-to-date")
        return cls(response)

    @classmethod
    async def open_when_unauthorized(cls, client: AsyncFlaskClient, reference: str) -> ForbiddenPage:
        response = await client.get(f"/schemes/{reference}/spend-to-date")
        return ForbiddenPage(response)

    @classmethod
    async def open_when_not_found(cls, client: AsyncFlaskClient, reference: str) -> NotFoundPage:
        response = await client.get(f"/schemes/{reference}/spend-to-date")
        return NotFoundPage(response)


class ChangeMilestoneDatesFormComponent:
    def __init__(self, form: Tag):
        self.confirm_url = form["action"]
        self.feasibility_design_completed_planned = DateComponent(
            one(form.select("fieldset:has(legend:-soup-contains('Feasibility design completed Planned date'))"))
        )
        self.feasibility_design_completed_actual = DateComponent(
            one(form.select("fieldset:has(legend:-soup-contains('Feasibility design completed Actual date'))"))
        )
        self.preliminary_design_completed_planned = DateComponent(
            one(form.select("fieldset:has(legend:-soup-contains('Preliminary design completed Planned date'))"))
        )
        self.preliminary_design_completed_actual = DateComponent(
            one(form.select("fieldset:has(legend:-soup-contains('Preliminary design completed Actual date'))"))
        )
        self.detailed_design_completed_heading = one(
            form.select("h2:-soup-contains('Detailed design completed')")
        ).string
        self.detailed_design_completed_planned = DateComponent(
            one(form.select("fieldset:has(legend:-soup-contains('Detailed design completed Planned date'))"))
        )
        self.detailed_design_completed_actual = DateComponent(
            one(form.select("fieldset:has(legend:-soup-contains('Detailed design completed Actual date'))"))
        )
        self.construction_started_planned = DateComponent(
            one(form.select("fieldset:has(legend:-soup-contains('Construction started Planned date'))"))
        )
        self.construction_started_actual = DateComponent(
            one(form.select("fieldset:has(legend:-soup-contains('Construction started Actual date'))"))
        )
        self.construction_completed_planned = DateComponent(
            one(form.select("fieldset:has(legend:-soup-contains('Construction completed Planned date'))"))
        )
        self.construction_completed_actual = DateComponent(
            one(form.select("fieldset:has(legend:-soup-contains('Construction completed Actual date'))"))
        )
        self.cancel_url = one(form.select("a"))["href"]


class ChangeMilestoneDatesPage(PageObject):
    def __init__(self, response: TestResponse):
        super().__init__(response)
        alert = self._soup.select_one(".govuk-error-summary div[role='alert']")
        self.errors = ErrorSummaryComponent(alert) if alert else None
        self.important_notification = NotificationBannerComponent.for_important(self._soup)
        heading_tag = self._soup.select_one("main h1")
        self.heading = HeadingComponent(heading_tag) if heading_tag else None
        self.is_visible = self.heading.text == "Change milestone dates" if self.heading else False

    @property
    def back_url(self) -> str:
        return str(one(self._soup.select("a.govuk-back-link"))["href"])

    @property
    def form(self) -> ChangeMilestoneDatesFormComponent:
        return ChangeMilestoneDatesFormComponent(one(self._soup.select("form")))

    @classmethod
    async def open(cls, client: AsyncFlaskClient, reference: str) -> Self:
        response = await client.get(f"/schemes/{reference}/milestones")
        return cls(response)

    @classmethod
    async def open_when_unauthorized(cls, client: AsyncFlaskClient, reference: str) -> ForbiddenPage:
        response = await client.get(f"/schemes/{reference}/milestones")
        return ForbiddenPage(response)

    @classmethod
    async def open_when_not_found(cls, client: AsyncFlaskClient, reference: str) -> NotFoundPage:
        response = await client.get(f"/schemes/{reference}/milestones")
        return NotFoundPage(response)


class ErrorSummaryComponent:
    def __init__(self, alert: Tag):
        self._alert = alert

    def __iter__(self) -> Iterator[str]:
        return (listitem.text.strip() for listitem in self._alert.select("li"))


class NotificationBannerComponent:
    def __init__(self, banner: Tag):
        self.heading = (one(banner.select("p")).string or "").strip()

    @classmethod
    def for_important(cls, soup: BeautifulSoup) -> Self | None:
        tag = soup.select_one(".govuk-notification-banner:not(.govuk-notification-banner--success)")
        return cls(tag) if tag else None

    @classmethod
    def for_success(cls, soup: BeautifulSoup) -> Self | None:
        tag = soup.select_one(".govuk-notification-banner.govuk-notification-banner--success")
        return cls(tag) if tag else None


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
        assert isinstance(form_group, Tag)
        error_message = form_group.select_one(".govuk-error-message")
        self.error = error_message.text.strip() if error_message else None


class CheckboxComponent:
    def __init__(self, input_: Tag):
        self.name = input_["name"]
        self.value = input_.has_attr("checked")
        form_group = input_.find_parent("div", class_="govuk-form-group")
        assert isinstance(form_group, Tag)
        self.is_errored = "govuk-form-group--error" in form_group.get_attribute_list("class")
        error_message = form_group.select_one(".govuk-error-message")
        self.error = error_message.text.strip() if error_message else None


def one(tags: ResultSet[Tag]) -> Tag:
    (tag,) = tags
    return tag
