import re
from re import Pattern
from typing import Iterator, Self

from playwright.sync_api import Locator, Page


class PageObject:
    def __init__(self, page: Page):
        self._page = page

    @property
    def title(self) -> str:
        return self._page.title()


class LoginPage(PageObject):
    def __init__(self, page: Page):
        super().__init__(page)

    @property
    def is_visible(self) -> bool:
        return self._page.get_by_role("heading", name="Login").is_visible()


class ForbiddenPage(PageObject):
    def __init__(self, page: Page):
        super().__init__(page)

    @property
    def is_visible(self) -> bool:
        return self._page.get_by_role("heading", name="Forbidden").is_visible()


class SchemesPage(PageObject):
    def __init__(self, page: Page):
        super().__init__(page)
        self.header = ServiceHeaderComponent(page.get_by_role("banner"))
        self._main = page.get_by_role("main")
        self.success_notification = NotificationBannerComponent.for_success(page)
        self.important_notification = NotificationBannerComponent.for_important(page)
        self.heading = HeadingComponent(self._main.get_by_role("heading"))
        self.schemes = SchemesTableComponent(self._main.get_by_role("table"))

    @classmethod
    def open(cls, page: Page) -> Self:
        page.goto("/schemes")
        return cls(page)

    @classmethod
    def open_when_unauthenticated(cls, page: Page) -> LoginPage:
        cls.open(page)
        return LoginPage(page)

    @classmethod
    def open_when_unauthorized(cls, page: Page) -> ForbiddenPage:
        cls.open(page)
        return ForbiddenPage(page)


class StartPage(PageObject):
    def __init__(self, page: Page):
        super().__init__(page)
        self._start = page.get_by_role("button")
        self.footer = FooterComponent(page.get_by_role("contentinfo"))

    @classmethod
    def open(cls, page: Page) -> Self:
        page.goto("/")
        return cls(page)

    @classmethod
    def open_when_authenticated(cls, page: Page) -> SchemesPage:
        cls.open(page)
        return SchemesPage(page)

    @property
    def is_visible(self) -> bool:
        return self._page.get_by_role("heading", name="Schemes").is_visible()

    def start(self) -> SchemesPage:
        self._start.click()
        return SchemesPage(self._page)

    def start_when_unauthenticated(self) -> LoginPage:
        self.start()
        return LoginPage(self._page)


class PrivacyPage(PageObject):
    def __init__(self, page: Page):
        super().__init__(page)

    @property
    def is_visible(self) -> bool:
        return self._page.get_by_role("heading", name="Privacy notice").first.is_visible()


class AccessibilityPage(PageObject):
    def __init__(self, page: Page):
        super().__init__(page)

    @property
    def is_visible(self) -> bool:
        return self._page.get_by_role("heading", name="Accessibility statement").first.is_visible()


class CookiesPage(PageObject):
    def __init__(self, page: Page):
        super().__init__(page)

    @property
    def is_visible(self) -> bool:
        return self._page.get_by_role("heading", name="Cookies").first.is_visible()


class FooterComponent:
    def __init__(self, footer: Locator):
        self._footer = footer

    def privacy(self) -> PrivacyPage:
        self._footer.get_by_role("link", name="Privacy").click()
        return PrivacyPage(self._footer.page)

    def accessibility(self) -> AccessibilityPage:
        self._footer.get_by_role("link", name="Accessibility").click()
        return AccessibilityPage(self._footer.page)

    def cookies(self) -> CookiesPage:
        self._footer.get_by_role("link", name="Cookies").click()
        return CookiesPage(self._footer.page)


class ServiceHeaderComponent:
    def __init__(self, header: Locator):
        self._header = header

    def sign_out(self) -> StartPage:
        self._header.get_by_role("link", name="Sign out").click()
        return StartPage(self._header.page)


class NotificationBannerComponent:
    def __init__(self, banner: Locator):
        self._heading = banner.get_by_role("paragraph")

    @property
    def heading(self) -> str:
        return (self._heading.text_content() or "").strip()

    @classmethod
    def for_important(cls, page: Page) -> Self:
        return cls(page.get_by_role("region", name="Important"))

    @classmethod
    def for_success(cls, page: Page) -> Self:
        return cls(page.get_by_role("alert", name="Success"))


class HeadingComponent:
    def __init__(self, heading: Locator):
        self._caption = heading.locator(".govuk-caption-xl")
        self._text = heading.locator("span").nth(1)

    @property
    def caption(self) -> str | None:
        return self._caption.text_content()

    @property
    def text(self) -> str | None:
        return self._text.text_content()


class SchemePage(PageObject):
    def __init__(self, page: Page):
        super().__init__(page)
        self._main = page.get_by_role("main")
        self.errors = ErrorSummaryComponent(page.get_by_role("alert"))
        self.heading = HeadingComponent(self._main.get_by_role("heading").first)
        self._inset_text = InsetTextComponent(self._main.locator(".govuk-inset-text"))
        self.overview = SchemeOverviewComponent(self._main.get_by_role("heading", name="Overview"))
        self.funding = SchemeFundingComponent(self._main.get_by_role("heading", name="Funding"))
        self.milestones = SchemeMilestonesComponent(self._main.get_by_role("heading", name="Milestones"))
        self.outputs = SchemeOutputsComponent(self._main.get_by_role("heading", name="Outputs"))
        self.review = SchemeReviewComponent(self._main.get_by_role("heading", name="Is this scheme up-to-date?"))

    @classmethod
    def open(cls, page: Page, reference: str) -> Self:
        # TODO: redirect to requested page after login - workaround, use homepage to complete authentication
        page.goto("/schemes")
        page.goto(f"/schemes/{reference}")
        return cls(page)

    @property
    def needs_review(self) -> bool:
        return self._inset_text.has_text(
            re.compile(r"Needs review\s+Check the details before confirming that this scheme is up-to-date.")
        )


class SchemeRowComponent:
    def __init__(self, row: Locator):
        self._row = row
        self._cells = row.get_by_role("cell")
        self._reference = self._cells.nth(0)
        name_cell = self._cells.nth(2)
        self._name = name_cell.locator("span")
        self._tag = TagComponent(name_cell.locator(".govuk-tag"))

    @property
    def reference(self) -> str | None:
        return self._reference.text_content()

    @property
    def funding_programme(self) -> str | None:
        return self._cells.nth(1).text_content()

    @property
    def name(self) -> str | None:
        return self._name.text_content()

    @property
    def needs_review(self) -> bool:
        return self._tag.text == "Needs review"

    @property
    def last_reviewed(self) -> str | None:
        return self._cells.nth(3).text_content()

    def open(self) -> SchemePage:
        self._reference.get_by_role("link").click()
        return SchemePage(self._row.page)

    def to_dict(self) -> dict[str, str | bool | None]:
        return {
            "reference": self.reference,
            "funding_programme": self.funding_programme,
            "name": self.name,
            "needs_review": self.needs_review,
            "last_reviewed": self.last_reviewed,
        }


class SchemesTableComponent:
    def __init__(self, table: Locator):
        self._rows = table.get_by_role("row")

    def __iter__(self) -> Iterator[SchemeRowComponent]:
        self._rows.first.wait_for()
        return (SchemeRowComponent(row) for row in self._rows.all()[1:])

    def __getitem__(self, reference: str) -> SchemeRowComponent:
        return next((scheme for scheme in self if scheme.reference == reference))

    def to_dicts(self) -> list[dict[str, str | bool | None]]:
        return [scheme.to_dict() for scheme in self]


class TagComponent:
    def __init__(self, tag: Locator):
        self._tag = tag

    @property
    def text(self) -> str:
        self._tag.first.wait_for()
        texts = self._tag.all_text_contents()
        return texts[0].strip() if texts else ""


class InsetTextComponent:
    def __init__(self, inset_text: Locator):
        self._inset_text = inset_text

    @property
    def text(self) -> str:
        return (self._inset_text.text_content() or "").strip()

    def has_text(self, pattern: Pattern[str]) -> bool:
        return pattern.match(self.text) is not None


class SummaryCardComponent:
    def __init__(self, title: Locator):
        self._card = title.locator("xpath=../..")

    def _get_definition(self, term_text: str) -> Locator:
        row = self._card.locator(".govuk-summary-list__row").filter(
            has=self._card.page.get_by_role("term").filter(has_text=term_text)
        )
        return row.get_by_role("definition")


class SchemeOverviewComponent(SummaryCardComponent):
    def __init__(self, title: Locator):
        super().__init__(title)
        self._reference = self._get_definition("Reference")
        self._scheme_type = self._get_definition("Scheme type")
        self._funding_programme = self._get_definition("Funding programme")
        self._current_milestone = self._get_definition("Current milestone")

    @property
    def reference(self) -> str:
        return (self._reference.text_content() or "").strip()

    @property
    def scheme_type(self) -> str:
        return (self._scheme_type.text_content() or "").strip()

    @property
    def funding_programme(self) -> str:
        return (self._funding_programme.text_content() or "").strip()

    @property
    def current_milestone(self) -> str:
        return (self._current_milestone.text_content() or "").strip()


class ChangeSpendToDatePage(PageObject):
    def __init__(self, page: Page):
        super().__init__(page)
        self.errors = ErrorSummaryComponent(page.get_by_role("alert"))
        self.form = ChangeSpendToDateFormComponent(page.get_by_role("form"))


class SchemeFundingComponent(SummaryCardComponent):
    def __init__(self, title: Locator):
        super().__init__(title)
        self._title = title
        self._funding_allocation = self._get_definition("Funding allocation")
        self._spend_to_date = self._get_definition("Spend to date").first
        self._change_spend_to_date = self._get_definition("Spend to date").nth(1)
        self._allocation_still_to_spend = self._get_definition("Allocation still to spend")

    @property
    def funding_allocation(self) -> str:
        return (self._funding_allocation.text_content() or "").strip()

    @property
    def spend_to_date(self) -> str:
        return (self._spend_to_date.text_content() or "").strip()

    def change_spend_to_date(self) -> ChangeSpendToDatePage:
        self._change_spend_to_date.click()
        return ChangeSpendToDatePage(self._title.page)

    @property
    def allocation_still_to_spend(self) -> str:
        return (self._allocation_still_to_spend.text_content() or "").strip()


class ChangeMilestoneDatesPage(PageObject):
    def __init__(self, page: Page):
        super().__init__(page)
        self.errors = ErrorSummaryComponent(page.get_by_role("alert"))
        self.form = ChangeMilestoneDatesFormComponent(page.get_by_role("form"))


class SchemeMilestonesComponent:
    def __init__(self, title: Locator):
        self._title = title
        title_wrapper = title.locator("xpath=..")
        card = title_wrapper.locator("xpath=..")
        self._change_milestone_dates = title_wrapper.get_by_role("link", name="Change")
        self.milestones = SchemeMilestonesTableComponent(card.get_by_role("table"))

    def change_milestone_dates(self) -> ChangeMilestoneDatesPage:
        self._change_milestone_dates.click()
        return ChangeMilestoneDatesPage(self._title.page)


class SchemeMilestoneRowComponent:
    def __init__(self, row: Locator):
        self._header = row.get_by_role("rowheader")
        self._cells = row.get_by_role("cell")

    @property
    def milestone(self) -> str | None:
        return self._header.text_content()

    @property
    def planned(self) -> str | None:
        return self._cells.nth(0).text_content()

    @property
    def actual(self) -> str | None:
        return self._cells.nth(1).text_content()

    def to_dict(self) -> dict[str, str | None]:
        return {"milestone": self.milestone, "planned": self.planned, "actual": self.actual}


class SchemeMilestonesTableComponent:
    def __init__(self, table: Locator):
        self._rows = table.get_by_role("row")

    def __iter__(self) -> Iterator[SchemeMilestoneRowComponent]:
        self._rows.first.wait_for()
        return (SchemeMilestoneRowComponent(row) for row in self._rows.all()[1:])

    def __getitem__(self, milestone: str) -> SchemeMilestoneRowComponent:
        return next(row for row in self if row.milestone == milestone)

    def to_dicts(self) -> list[dict[str, str | None]]:
        return [milestone.to_dict() for milestone in self]


class SchemeOutputsComponent:
    def __init__(self, title: Locator):
        card = title.locator("xpath=../..")
        self.outputs = SchemeOutputsTableComponent(card.get_by_role("table"))


class SchemeOutputRowComponent:
    def __init__(self, row: Locator):
        self._cells = row.get_by_role("cell")

    @property
    def infrastructure(self) -> str | None:
        return self._cells.nth(0).text_content()

    @property
    def measurement(self) -> str | None:
        return self._cells.nth(1).text_content()

    @property
    def planned(self) -> str | None:
        return self._cells.nth(2).text_content()

    def to_dict(self) -> dict[str, str | None]:
        return {
            "infrastructure": self.infrastructure,
            "measurement": self.measurement,
            "planned": self.planned,
        }


class SchemeOutputsTableComponent:
    def __init__(self, table: Locator):
        self._rows = table.get_by_role("row")

    def __iter__(self) -> Iterator[SchemeOutputRowComponent]:
        self._rows.first.wait_for()
        return (SchemeOutputRowComponent(row) for row in self._rows.all()[1:])

    def to_dicts(self) -> list[dict[str, str | None]]:
        return [output.to_dict() for output in self]


class SchemeReviewComponent:
    def __init__(self, heading: Locator):
        section = heading.locator("xpath=..")
        self.form = SchemeReviewFormComponent(section.get_by_role("form"))


class SchemeReviewFormComponent:
    def __init__(self, form: Locator):
        self._form = form
        self.up_to_date = CheckboxComponent(
            form.get_by_label("I confirm that the details in this scheme have been reviewed and are all up-to-date")
        )
        self._confirm = form.get_by_role("button", name="Confirm")

    def check_up_to_date(self) -> Self:
        self.up_to_date.value = True
        return self

    def confirm(self) -> SchemesPage:
        self._confirm.click()
        return SchemesPage(self._form.page)

    def confirm_when_error(self) -> SchemePage:
        self._confirm.click()
        return SchemePage(self._form.page)


class ChangeSpendToDateFormComponent:
    def __init__(self, form: Locator):
        self._form = form
        self.amount = TextComponent(form.get_by_label("How much has been spent to date?"))
        self._confirm = form.get_by_role("button", name="Confirm")

    def enter_amount(self, value: str) -> Self:
        self.amount.value = value
        return self

    def confirm(self) -> SchemePage:
        self._confirm.click()
        return SchemePage(self._form.page)

    def confirm_when_error(self) -> ChangeSpendToDatePage:
        self._confirm.click()
        return ChangeSpendToDatePage(self._form.page)


class ChangeMilestoneDatesFormComponent:
    def __init__(self, form: Locator):
        self._form = form
        self.construction_started_actual = DateComponent(
            form.get_by_role("group", name="Construction started Actual date")
        )
        self.construction_completed_planned = DateComponent(
            form.get_by_role("group", name="Construction completed Planned date")
        )
        self._confirm = form.get_by_role("button", name="Confirm")

    def enter_construction_started_actual(self, value: str) -> Self:
        self.construction_started_actual.value = value
        return self

    def enter_construction_completed_planned(self, value: str) -> Self:
        self.construction_completed_planned.value = value
        return self

    def confirm(self) -> SchemePage:
        self._confirm.click()
        return SchemePage(self._form.page)

    def confirm_when_error(self) -> ChangeMilestoneDatesPage:
        self._confirm.click()
        return ChangeMilestoneDatesPage(self._form.page)


class DateComponent:
    def __init__(self, fieldset: Locator):
        form_group = fieldset.locator("xpath=..")
        self.day = TextComponent(fieldset.get_by_label("Day"))
        self.month = TextComponent(fieldset.get_by_label("Month"))
        self.year = TextComponent(fieldset.get_by_label("Year"))
        self._error = form_group.locator(".govuk-error-message")

    @property
    def value(self) -> str:
        return f"{self.day.value} {self.month.value} {self.year.value}"

    @value.setter
    def value(self, value: str) -> None:
        values = value.split(" ")
        self.day.value = values[0]
        self.month.value = values[1]
        self.year.value = values[2]

    @property
    def is_errored(self) -> bool:
        return self.day.is_errored and self.month.is_errored and self.year.is_errored

    @property
    def error(self) -> str | None:
        text_content = self._error.text_content()
        return text_content.strip() if text_content else None


class ErrorSummaryComponent:
    def __init__(self, alert: Locator):
        self._listitems = alert.get_by_role("listitem")

    def __iter__(self) -> Iterator[str]:
        self._listitems.first.wait_for()
        return (text_content.strip() for text_content in self._listitems.all_text_contents())


class TextComponent:
    def __init__(self, input_: Locator):
        self._input = input_
        form_group = input_.locator("xpath=../..")
        self._error = form_group.locator(".govuk-error-message")

    @property
    def value(self) -> str:
        return self._input.input_value()

    @value.setter
    def value(self, value: str) -> None:
        self._input.fill(value)

    @property
    def is_errored(self) -> bool:
        return "govuk-input--error" in (self._input.get_attribute("class") or "").split(" ")

    @property
    def error(self) -> str | None:
        text_content = self._error.text_content()
        return text_content.strip() if text_content else None


class CheckboxComponent:
    def __init__(self, input_: Locator):
        self._input = input_
        self._form_group = input_.locator("xpath=../../..")
        self._error = self._form_group.locator(".govuk-error-message")

    @property
    def value(self) -> bool:
        return self._input.is_checked()

    @value.setter
    def value(self, value: bool) -> None:
        self._input.set_checked(value)

    @property
    def is_errored(self) -> bool:
        return "govuk-form-group--error" in (self._form_group.get_attribute("class") or "").split(" ")

    @property
    def error(self) -> str | None:
        text_content = self._error.text_content()
        return text_content.strip() if text_content else None
