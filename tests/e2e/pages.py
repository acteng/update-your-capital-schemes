from __future__ import annotations

from typing import Iterator

from playwright.sync_api import Locator, Page


class StartPage:
    def __init__(self, page: Page):
        self._page = page
        self._start = page.get_by_role("button")

    def open(self) -> StartPage:
        self._page.goto("/")
        return self

    def open_when_authenticated(self) -> SchemesPage:
        self.open()
        return SchemesPage(self._page)

    @property
    def is_visible(self) -> bool:
        return self._page.get_by_role("heading", name="Schemes").is_visible()

    def start(self) -> SchemesPage:
        self._start.click()
        return SchemesPage(self._page)

    def start_when_unauthenticated(self) -> LoginPage:
        self.start()
        return LoginPage(self._page)


class LoginPage:
    def __init__(self, page: Page):
        self._page = page

    @property
    def is_visible(self) -> bool:
        return self._page.get_by_role("heading", name="Login").is_visible()


class UnauthorizedPage:
    def __init__(self, page: Page):
        self._page = page

    @property
    def is_visible(self) -> bool:
        return self._page.get_by_role("heading", name="Unauthorised").is_visible()


class SchemesPage:
    def __init__(self, page: Page):
        self._page = page
        self.header = ServiceHeaderComponent(page.get_by_role("banner"))
        self._main = page.get_by_role("main")
        self._authority = self._main.get_by_role("heading")
        self.schemes = SchemesTableComponent(page, self._main.get_by_role("table"))

    def open(self) -> SchemesPage:
        self._page.goto("/schemes")
        return self

    def open_when_unauthenticated(self) -> LoginPage:
        self.open()
        return LoginPage(self._page)

    def open_when_unauthorized(self) -> UnauthorizedPage:
        self.open()
        return UnauthorizedPage(self._page)

    @property
    def authority(self) -> str | None:
        return self._authority.text_content()


class ServiceHeaderComponent:
    def __init__(self, component: Locator):
        self._component = component

    def sign_out(self) -> StartPage:
        self._component.get_by_role("link", name="Sign out").click()
        return StartPage(self._component.page)


class SchemesTableComponent:
    def __init__(self, page: Page, component: Locator):
        self._page = page
        self._rows = component.get_by_role("row")

    def __iter__(self) -> Iterator[SchemeRowComponent]:
        return iter([SchemeRowComponent(self._page, row) for row in self._rows.all()[1:]])

    def __getitem__(self, reference: str) -> SchemeRowComponent:
        return next((scheme for scheme in self if scheme.reference == reference))

    def to_dicts(self) -> list[dict[str, str | None]]:
        return [scheme.to_dict() for scheme in self]


class SchemeRowComponent:
    def __init__(self, page: Page, component: Locator):
        self._page = page
        self._cells = component.get_by_role("cell")
        self._reference = self._cells.nth(0)

    @property
    def reference(self) -> str | None:
        return self._reference.text_content()

    @property
    def funding_programme(self) -> str | None:
        return self._cells.nth(1).text_content()

    @property
    def name(self) -> str | None:
        return self._cells.nth(2).text_content()

    def open(self) -> SchemePage:
        self._reference.get_by_role("link").click()
        return SchemePage(self._page)

    def to_dict(self) -> dict[str, str | None]:
        return {"reference": self.reference, "funding_programme": self.funding_programme, "name": self.name}


class SchemePage:
    def __init__(self, page: Page):
        self._page = page
        self._main = page.get_by_role("main")
        self._name = self._main.get_by_role("heading").nth(0)
        self.overview = SchemeOverviewComponent(self._main.get_by_role("tabpanel", name="Overview"))
        self._funding_tab = self._main.get_by_role("tab", name="Funding")
        self.funding = SchemeFundingComponent(self._main.get_by_role("tabpanel", name="Funding"))
        self._milestones_tab = self._main.get_by_role("tab", name="Milestones")
        self.milestones = SchemeMilestonesComponent(self._main.get_by_role("tabpanel", name="Milestones"))
        self._outputs_tab = self._main.get_by_role("tab", name="Outputs")
        self.outputs = SchemeOutputsComponent(self._main.get_by_role("tabpanel", name="Outputs"))

    def open(self, id_: int) -> SchemePage:
        # TODO: redirect to requested page after login - workaround, use homepage to complete authentication
        self._page.goto("/schemes")
        self._page.goto(f"/schemes/{id_}")
        return self

    @property
    def name(self) -> str | None:
        return self._name.text_content()

    def open_funding(self) -> SchemeFundingComponent:
        self._funding_tab.click()
        return self.funding

    def open_milestones(self) -> SchemeMilestonesComponent:
        self._milestones_tab.click()
        return self.milestones

    def open_outputs(self) -> SchemeOutputsComponent:
        self._outputs_tab.click()
        return self.outputs


class SchemeOverviewComponent:
    def __init__(self, component: Locator):
        self._reference = component.get_by_role("definition").nth(0)
        self._scheme_type = component.get_by_role("definition").nth(1)
        self._funding_programme = component.get_by_role("definition").nth(2)
        self._current_milestone = component.get_by_role("definition").nth(3)

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


class SchemeFundingComponent:
    def __init__(self, component: Locator):
        self._funding_allocation = component.get_by_role("definition").nth(0)
        self._spend_to_date = component.get_by_role("definition").nth(1)
        self._change_control_adjustment = component.get_by_role("definition").nth(2)
        self._allocation_still_to_spend = component.get_by_role("definition").nth(3)

    @property
    def funding_allocation(self) -> str:
        return (self._funding_allocation.text_content() or "").strip()

    @property
    def spend_to_date(self) -> str:
        return (self._spend_to_date.text_content() or "").strip()

    @property
    def change_control_adjustment(self) -> str:
        return (self._change_control_adjustment.text_content() or "").strip()

    @property
    def allocation_still_to_spend(self) -> str:
        return (self._allocation_still_to_spend.text_content() or "").strip()


class SchemeMilestonesComponent:
    def __init__(self, component: Locator):
        self.milestones = SchemeMilestonesTableComponent(component.get_by_role("table"))


class SchemeMilestonesTableComponent:
    def __init__(self, component: Locator):
        self._rows = component.get_by_role("row")

    def __iter__(self) -> Iterator[SchemeMilestoneRowComponent]:
        return iter([SchemeMilestoneRowComponent(row) for row in self._rows.all()[1:]])

    def to_dicts(self) -> list[dict[str, str | None]]:
        return [milestone.to_dict() for milestone in self]


class SchemeMilestoneRowComponent:
    def __init__(self, component: Locator):
        self._header = component.get_by_role("rowheader")
        self._cells = component.get_by_role("cell")

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


class SchemeOutputsComponent:
    def __init__(self, component: Locator):
        self.outputs = SchemeOutputsTableComponent(component.get_by_role("table"))


class SchemeOutputsTableComponent:
    def __init__(self, component: Locator):
        self._rows = component.get_by_role("row")

    def __iter__(self) -> Iterator[SchemeOutputRowComponent]:
        return iter([SchemeOutputRowComponent(row) for row in self._rows.all()[1:]])

    def to_dicts(self) -> list[dict[str, str | None]]:
        return [output.to_dict() for output in self]


class SchemeOutputRowComponent:
    def __init__(self, component: Locator):
        self._cells = component.get_by_role("cell")

    @property
    def infrastructure(self) -> str | None:
        return self._cells.nth(0).text_content()

    @property
    def measurement(self) -> str | None:
        return self._cells.nth(1).text_content()

    @property
    def planned(self) -> str | None:
        return self._cells.nth(2).text_content()

    @property
    def actual(self) -> str | None:
        return self._cells.nth(3).text_content()

    @property
    def planned_outputs_not_yet_delivered(self) -> str | None:
        return self._cells.nth(4).text_content()

    @property
    def output_delivery_status(self) -> str | None:
        return self._cells.nth(5).text_content()

    def to_dict(self) -> dict[str, str | None]:
        return {
            "infrastructure": self.infrastructure,
            "measurement": self.measurement,
            "planned": self.planned,
            "actual": self.actual,
            "planned_outputs_not_yet_delivered": self.planned_outputs_not_yet_delivered,
            "output_delivery_status": self.output_delivery_status,
        }
