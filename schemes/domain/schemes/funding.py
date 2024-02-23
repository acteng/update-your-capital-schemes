from __future__ import annotations

from datetime import datetime
from enum import Enum, auto, unique

from schemes.domain.schemes.dates import DateRange


class SchemeFunding:
    def __init__(self) -> None:
        self._financial_revisions: list[FinancialRevision] = []

    @property
    def financial_revisions(self) -> list[FinancialRevision]:
        return list(self._financial_revisions)

    def update_financial(self, financial_revision: FinancialRevision) -> None:
        if financial_revision.is_current_funding_allocation:
            self._ensure_no_current_funding_allocation()

        if financial_revision.is_current_spent_to_date:
            self._ensure_no_current_spent_to_date()

        self._financial_revisions.append(financial_revision)

    def update_financials(self, *financial_revisions: FinancialRevision) -> None:
        for financial_revision in financial_revisions:
            self.update_financial(financial_revision)

    def _ensure_no_current_funding_allocation(self) -> None:
        current_funding_allocation = next(
            (revision for revision in self._financial_revisions if revision.is_current_funding_allocation), None
        )
        if current_funding_allocation:
            raise ValueError(f"Current funding allocation already exists: {current_funding_allocation}")

    def _ensure_no_current_spent_to_date(self) -> None:
        current_spent_to_date = self._current_spent_to_date
        if current_spent_to_date:
            raise ValueError(f"Current spent to date already exists: {current_spent_to_date}")

    @property
    def _current_spent_to_date(self) -> FinancialRevision | None:
        return next((revision for revision in self._financial_revisions if revision.is_current_spent_to_date), None)

    def update_spend_to_date(self, now: datetime, amount: int) -> None:
        current_spent_to_date = self._current_spent_to_date
        if current_spent_to_date:
            current_spent_to_date.effective = DateRange(current_spent_to_date.effective.date_from, now)

        self.update_financial(
            FinancialRevision(
                id_=None,
                effective=DateRange(now, None),
                type_=FinancialType.SPENT_TO_DATE,
                amount=amount,
                source=DataSource.AUTHORITY_UPDATE,
            )
        )

    @property
    def funding_allocation(self) -> int | None:
        amounts = (revision.amount for revision in self._financial_revisions if revision.is_current_funding_allocation)
        return next(amounts, None)

    @property
    def change_control_adjustment(self) -> int | None:
        amounts = [
            revision.amount
            for revision in self._financial_revisions
            if revision.type == FinancialType.FUNDING_ALLOCATION
            and revision.source == DataSource.CHANGE_CONTROL
            and revision.effective.date_to is None
        ]
        return sum(amounts) if amounts else None

    @property
    def spend_to_date(self) -> int | None:
        amounts = (revision.amount for revision in self._financial_revisions if revision.is_current_spent_to_date)
        return next(amounts, None)

    @property
    def adjusted_funding_allocation(self) -> int:
        funding_allocation = self.funding_allocation or 0
        change_control_adjustment = self.change_control_adjustment or 0
        return funding_allocation + change_control_adjustment

    @property
    def allocation_still_to_spend(self) -> int:
        spend_to_date = self.spend_to_date or 0
        return self.adjusted_funding_allocation - spend_to_date


class FinancialRevision:
    # TODO: domain identifier should be mandatory for transient instances
    def __init__(self, id_: int | None, effective: DateRange, type_: FinancialType, amount: int, source: DataSource):
        self.id = id_
        self.effective = effective
        self.type = type_
        self.amount = amount
        self.source = source

    @property
    def is_current_funding_allocation(self) -> bool:
        return (
            self.type == FinancialType.FUNDING_ALLOCATION
            and self.source != DataSource.CHANGE_CONTROL
            and self.effective.date_to is None
        )

    @property
    def is_current_spent_to_date(self) -> bool:
        return self.type == FinancialType.SPENT_TO_DATE and self.effective.date_to is None


@unique
class FinancialType(Enum):
    EXPECTED_COST = auto()
    ACTUAL_COST = auto()
    FUNDING_ALLOCATION = auto()
    SPENT_TO_DATE = auto()
    FUNDING_REQUEST = auto()


@unique
class DataSource(Enum):
    PULSE_5 = auto()
    PULSE_6 = auto()
    ATF4_BID = auto()
    ATF3_BID = auto()
    INSPECTORATE_REVIEW = auto()
    REGIONAL_MANAGER_REQUEST = auto()
    INVESTMENT_TEAM_REQUEST = auto()
    ATE_PUBLISHED_DATA = auto()
    CHANGE_CONTROL = auto()
    ATF4E_BID = auto()
    ATF4E_MODERATION = auto()
    PULSE_2023_24_Q2 = auto()
    PULSE_2023_24_Q3 = auto()
    PULSE_2023_24_Q4 = auto()
    INITIAL_SCHEME_LIST = auto()
    AUTHORITY_UPDATE = auto()
    PULSE_2023_24_Q2_DATA_CLEANSE = auto()
