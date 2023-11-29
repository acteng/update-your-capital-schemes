from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from _decimal import Decimal

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
        current_spent_to_date = next(
            (revision for revision in self._financial_revisions if revision.is_current_spent_to_date), None
        )
        if current_spent_to_date:
            raise ValueError(f"Current spent to date already exists: {current_spent_to_date}")

    @property
    def funding_allocation(self) -> Decimal | None:
        amounts = (revision.amount for revision in self._financial_revisions if revision.is_current_funding_allocation)
        return next(amounts, None)

    @property
    def spend_to_date(self) -> Decimal | None:
        amounts = (revision.amount for revision in self._financial_revisions if revision.is_current_spent_to_date)
        return next(amounts, None)

    @property
    def change_control_adjustment(self) -> Decimal | None:
        amounts = [
            revision.amount
            for revision in self._financial_revisions
            if revision.type == FinancialType.FUNDING_ALLOCATION
            and revision.source == DataSource.CHANGE_CONTROL
            and revision.effective.date_to is None
        ]
        return sum(amounts, Decimal(0)) if amounts else None

    @property
    def allocation_still_to_spend(self) -> Decimal:
        funding_allocation = self.funding_allocation or Decimal(0)
        spend_to_date = self.spend_to_date or Decimal(0)
        change_control_adjustment = self.change_control_adjustment or Decimal(0)
        return funding_allocation + change_control_adjustment - spend_to_date


@dataclass(frozen=True)
class FinancialRevision:
    effective: DateRange
    type: FinancialType
    amount: Decimal
    source: DataSource

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


class FinancialType(Enum):
    EXPECTED_COST = auto()
    ACTUAL_COST = auto()
    FUNDING_ALLOCATION = auto()
    SPENT_TO_DATE = auto()
    FUNDING_REQUEST = auto()


class DataSource(Enum):
    PULSE_5 = auto()
    PULSE_6 = auto()
    ATF4_BID = auto()
    ATF3_BID = auto()
    INSPECTORATE_REVIEW = auto()
    REGIONAL_ENGAGEMENT_MANAGER_REVIEW = auto()
    ATE_PUBLISHED_DATA = auto()
    CHANGE_CONTROL = auto()
    ATF4E_BID = auto()
    PULSE_2023_24_Q2 = auto()
    INITIAL_SCHEME_LIST = auto()
