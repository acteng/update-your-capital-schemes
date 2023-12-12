from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum, unique

from schemes.domain.schemes import (
    DataSource,
    DateRange,
    FinancialRevision,
    FinancialType,
    SchemeFunding,
)


@dataclass(frozen=True)
class SchemeFundingContext:
    funding_allocation: Decimal | None
    spend_to_date: Decimal | None
    change_control_adjustment: Decimal | None
    allocation_still_to_spend: Decimal

    @classmethod
    def from_domain(cls, funding: SchemeFunding) -> SchemeFundingContext:
        return cls(
            funding_allocation=funding.funding_allocation,
            spend_to_date=funding.spend_to_date,
            change_control_adjustment=funding.change_control_adjustment,
            allocation_still_to_spend=funding.allocation_still_to_spend,
        )


@dataclass(frozen=True)
class FinancialRevisionRepr:
    effective_date_from: str
    effective_date_to: str | None
    type: FinancialTypeRepr
    amount: str
    source: DataSourceRepr

    def to_domain(self) -> FinancialRevision:
        return FinancialRevision(
            effective=DateRange(
                date_from=date.fromisoformat(self.effective_date_from),
                date_to=date.fromisoformat(self.effective_date_to) if self.effective_date_to else None,
            ),
            type=self.type.to_domain(),
            amount=Decimal(self.amount),
            source=self.source.to_domain(),
        )


@unique
class FinancialTypeRepr(Enum):
    EXPECTED_COST = "expected cost"
    ACTUAL_COST = "actual cost"
    FUNDING_ALLOCATION = "funding allocation"
    SPENT_TO_DATE = "spent to date"
    FUNDING_REQUEST = "funding request"

    def to_domain(self) -> FinancialType:
        members = {
            FinancialTypeRepr.EXPECTED_COST: FinancialType.EXPECTED_COST,
            FinancialTypeRepr.ACTUAL_COST: FinancialType.ACTUAL_COST,
            FinancialTypeRepr.FUNDING_ALLOCATION: FinancialType.FUNDING_ALLOCATION,
            FinancialTypeRepr.SPENT_TO_DATE: FinancialType.SPENT_TO_DATE,
            FinancialTypeRepr.FUNDING_REQUEST: FinancialType.FUNDING_REQUEST,
        }
        return members[self]


@unique
class DataSourceRepr(Enum):
    PULSE_5 = "Pulse 5"
    PULSE_6 = "Pulse 6"
    ATF4_BID = "ATF4 Bid"
    ATF3_BID = "ATF3 Bid"
    INSPECTORATE_REVIEW = "Inspectorate review"
    REGIONAL_ENGAGEMENT_MANAGER_REVIEW = "Regional Engagement Manager review"
    ATE_PUBLISHED_DATA = "ATE published data"
    CHANGE_CONTROL = "change control"
    ATF4E_BID = "ATF4e Bid"
    ATF4E_MODERATION = "ATF4e Moderation"
    PULSE_2023_24_Q2 = "Pulse 2023/24 Q2"
    INITIAL_SCHEME_LIST = "Initial Scheme List"

    def to_domain(self) -> DataSource:
        members = {
            DataSourceRepr.PULSE_5: DataSource.PULSE_5,
            DataSourceRepr.PULSE_6: DataSource.PULSE_6,
            DataSourceRepr.ATF4_BID: DataSource.ATF4_BID,
            DataSourceRepr.ATF3_BID: DataSource.ATF3_BID,
            DataSourceRepr.INSPECTORATE_REVIEW: DataSource.INSPECTORATE_REVIEW,
            DataSourceRepr.REGIONAL_ENGAGEMENT_MANAGER_REVIEW: DataSource.REGIONAL_ENGAGEMENT_MANAGER_REVIEW,
            DataSourceRepr.ATE_PUBLISHED_DATA: DataSource.ATE_PUBLISHED_DATA,
            DataSourceRepr.CHANGE_CONTROL: DataSource.CHANGE_CONTROL,
            DataSourceRepr.ATF4E_BID: DataSource.ATF4E_BID,
            DataSourceRepr.ATF4E_MODERATION: DataSource.ATF4E_MODERATION,
            DataSourceRepr.PULSE_2023_24_Q2: DataSource.PULSE_2023_24_Q2,
            DataSourceRepr.INITIAL_SCHEME_LIST: DataSource.INITIAL_SCHEME_LIST,
        }
        return members[self]
