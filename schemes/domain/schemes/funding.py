from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from _decimal import Decimal

from schemes.domain.schemes.dates import DateRange


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
