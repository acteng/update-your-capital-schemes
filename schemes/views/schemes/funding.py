from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum, unique

from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovTextInput
from wtforms.validators import InputRequired, NumberRange, ValidationError

from schemes.dicts import inverse_dict
from schemes.domain.dates import DateRange
from schemes.domain.schemes import (
    FinancialRevision,
    FinancialType,
    Scheme,
    SchemeFunding,
)
from schemes.views.forms import CustomMessageIntegerField
from schemes.views.schemes.data_source import DataSourceRepr


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
class ChangeSpendToDateContext:
    id: int
    funding_allocation: int | None
    change_control_adjustment: int | None
    form: ChangeSpendToDateForm

    @classmethod
    def from_domain(cls, scheme: Scheme) -> ChangeSpendToDateContext:
        return cls(
            id=scheme.id,
            funding_allocation=scheme.funding.funding_allocation,
            change_control_adjustment=scheme.funding.change_control_adjustment,
            form=ChangeSpendToDateForm.from_domain(scheme.funding),
        )


class ChangeSpendToDateForm(FlaskForm):  # type: ignore
    amount = CustomMessageIntegerField(
        widget=GovTextInput(),
        validators=[
            InputRequired(message="Enter spend to date"),
            NumberRange(min=0, message="Spend to date must be £0 or more"),
        ],
        invalid_message="Spend to date must be a number",
    )

    def __init__(self, max_amount: int, **kwargs: object):
        super().__init__(**kwargs)
        self.max_amount = max_amount

    @classmethod
    def from_domain(cls, funding: SchemeFunding) -> ChangeSpendToDateForm:
        return cls(max_amount=funding.adjusted_funding_allocation, data={"amount": funding.spend_to_date})

    def update_domain(self, funding: SchemeFunding, now: datetime) -> None:
        assert self.amount.data is not None
        funding.update_spend_to_date(now=now, amount=self.amount.data)

    @staticmethod
    def validate_amount(form: ChangeSpendToDateForm, field: CustomMessageIntegerField) -> None:
        if field.data is not None and field.data > form.max_amount:
            raise ValidationError(f"Spend to date must be £{form.max_amount:,} or less")


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
            effective_date_to=(
                financial_revision.effective.date_to.isoformat() if financial_revision.effective.date_to else None
            ),
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
