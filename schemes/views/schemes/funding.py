from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum, unique

from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovTextInput
from wtforms.fields.simple import StringField

from schemes.dicts import inverse_dict
from schemes.domain.schemes import (
    DataSource,
    DateRange,
    FinancialRevision,
    FinancialType,
    Scheme,
    SchemeFunding,
)


@dataclass(frozen=True)
class SchemeFundingContext:
    funding_allocation: int | None
    change_control_adjustment: int | None
    spend_to_date: int | None
    allocation_still_to_spend: int

    @classmethod
    def from_domain(cls, funding: SchemeFunding) -> SchemeFundingContext:
        return cls(
            funding_allocation=funding.funding_allocation,
            change_control_adjustment=funding.change_control_adjustment,
            spend_to_date=funding.spend_to_date,
            allocation_still_to_spend=funding.allocation_still_to_spend,
        )


@dataclass(frozen=True)
class SchemeChangeSpendToDateContext:
    id: int
    form: ChangeSpendToDateForm

    @classmethod
    def from_domain(cls, scheme: Scheme) -> SchemeChangeSpendToDateContext:
        return cls(id=scheme.id, form=ChangeSpendToDateForm.from_domain(scheme.funding))


class ChangeSpendToDateForm(FlaskForm):  # type: ignore
    amount = StringField(widget=GovTextInput())

    @classmethod
    def from_domain(cls, funding: SchemeFunding) -> ChangeSpendToDateForm:
        return cls(data={"amount": funding.spend_to_date})

    def update_domain(self, funding: SchemeFunding, now: datetime) -> None:
        amount = int(self.amount.data)
        funding.update_spend_to_date(now=now, amount=amount)


@dataclass(frozen=True)
class FinancialRevisionRepr:
    id: int
    effective_date_from: str
    effective_date_to: str | None
    type: FinancialTypeRepr
    amount: int
    source: DataSourceRepr

    @classmethod
    def from_domain(cls, financial_revision: FinancialRevision) -> FinancialRevisionRepr:
        if not financial_revision.id:
            raise ValueError("Financial revision must be persistent")

        return FinancialRevisionRepr(
            id=financial_revision.id,
            effective_date_from=financial_revision.effective.date_from.isoformat(),
            effective_date_to=financial_revision.effective.date_to.isoformat()
            if financial_revision.effective.date_to
            else None,
            type=FinancialTypeRepr.from_domain(financial_revision.type),
            amount=financial_revision.amount,
            source=DataSourceRepr.from_domain(financial_revision.source),
        )

    def to_domain(self) -> FinancialRevision:
        return FinancialRevision(
            id_=self.id,
            effective=DateRange(
                date_from=datetime.fromisoformat(self.effective_date_from),
                date_to=datetime.fromisoformat(self.effective_date_to) if self.effective_date_to else None,
            ),
            type_=self.type.to_domain(),
            amount=self.amount,
            source=self.source.to_domain(),
        )


@unique
class FinancialTypeRepr(Enum):
    EXPECTED_COST = "expected cost"
    ACTUAL_COST = "actual cost"
    FUNDING_ALLOCATION = "funding allocation"
    SPENT_TO_DATE = "spent to date"
    FUNDING_REQUEST = "funding request"

    @classmethod
    def from_domain(cls, financial_type: FinancialType) -> FinancialTypeRepr:
        return cls._members()[financial_type]

    def to_domain(self) -> FinancialType:
        return inverse_dict(self._members())[self]

    @staticmethod
    def _members() -> dict[FinancialType, FinancialTypeRepr]:
        return {
            FinancialType.EXPECTED_COST: FinancialTypeRepr.EXPECTED_COST,
            FinancialType.ACTUAL_COST: FinancialTypeRepr.ACTUAL_COST,
            FinancialType.FUNDING_ALLOCATION: FinancialTypeRepr.FUNDING_ALLOCATION,
            FinancialType.SPENT_TO_DATE: FinancialTypeRepr.SPENT_TO_DATE,
            FinancialType.FUNDING_REQUEST: FinancialTypeRepr.FUNDING_REQUEST,
        }


@unique
class DataSourceRepr(Enum):
    PULSE_5 = "Pulse 5"
    PULSE_6 = "Pulse 6"
    ATF4_BID = "ATF4 Bid"
    ATF3_BID = "ATF3 Bid"
    INSPECTORATE_REVIEW = "Inspectorate Review"
    REGIONAL_ENGAGEMENT_MANAGER_REVIEW = "Regional Engagement Manager Review"
    ATE_PUBLISHED_DATA = "ATE Published Data"
    CHANGE_CONTROL = "Change Control"
    ATF4E_BID = "ATF4e Bid"
    ATF4E_MODERATION = "ATF4e Moderation"
    PULSE_2023_24_Q2 = "Pulse 2023/24 Q2"
    INITIAL_SCHEME_LIST = "Initial Scheme List"
    AUTHORITY_UPDATE = "Authority Update"
    PULSE_2023_24_Q2_DATA_CLEANSE = "Pulse 2023/24 Q2 Data Cleanse"

    @classmethod
    def from_domain(cls, data_source: DataSource) -> DataSourceRepr:
        return cls._members()[data_source]

    def to_domain(self) -> DataSource:
        return inverse_dict(self._members())[self]

    @staticmethod
    def _members() -> dict[DataSource, DataSourceRepr]:
        return {
            DataSource.PULSE_5: DataSourceRepr.PULSE_5,
            DataSource.PULSE_6: DataSourceRepr.PULSE_6,
            DataSource.ATF4_BID: DataSourceRepr.ATF4_BID,
            DataSource.ATF3_BID: DataSourceRepr.ATF3_BID,
            DataSource.INSPECTORATE_REVIEW: DataSourceRepr.INSPECTORATE_REVIEW,
            DataSource.REGIONAL_ENGAGEMENT_MANAGER_REVIEW: DataSourceRepr.REGIONAL_ENGAGEMENT_MANAGER_REVIEW,
            DataSource.ATE_PUBLISHED_DATA: DataSourceRepr.ATE_PUBLISHED_DATA,
            DataSource.CHANGE_CONTROL: DataSourceRepr.CHANGE_CONTROL,
            DataSource.ATF4E_BID: DataSourceRepr.ATF4E_BID,
            DataSource.ATF4E_MODERATION: DataSourceRepr.ATF4E_MODERATION,
            DataSource.PULSE_2023_24_Q2: DataSourceRepr.PULSE_2023_24_Q2,
            DataSource.INITIAL_SCHEME_LIST: DataSourceRepr.INITIAL_SCHEME_LIST,
            DataSource.AUTHORITY_UPDATE: DataSourceRepr.AUTHORITY_UPDATE,
            DataSource.PULSE_2023_24_Q2_DATA_CLEANSE: DataSourceRepr.PULSE_2023_24_Q2_DATA_CLEANSE,
        }
