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
    BidStatus,
    BidStatusRevision,
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
    spend_to_date: int | None
    allocation_still_to_spend: int

    @classmethod
    def from_domain(cls, funding: SchemeFunding) -> SchemeFundingContext:
        return cls(
            funding_allocation=funding.funding_allocation,
            spend_to_date=funding.spend_to_date,
            allocation_still_to_spend=funding.allocation_still_to_spend,
        )


@dataclass(frozen=True)
class ChangeSpendToDateContext:
    id: int
    funding_allocation: int | None
    form: ChangeSpendToDateForm

    @classmethod
    def from_domain(cls, scheme: Scheme) -> ChangeSpendToDateContext:
        return cls(
            id=scheme.id,
            funding_allocation=scheme.funding.funding_allocation,
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
        funding_allocation = funding.funding_allocation or 0
        return cls(max_amount=funding_allocation, data={"amount": funding.spend_to_date})

    def update_domain(self, funding: SchemeFunding, now: datetime) -> None:
        assert self.amount.data is not None
        funding.update_spend_to_date(now=now, amount=self.amount.data)

    @staticmethod
    def validate_amount(form: ChangeSpendToDateForm, field: CustomMessageIntegerField) -> None:
        if field.data is not None and field.data > form.max_amount:
            raise ValidationError(f"Spend to date must be £{form.max_amount:,} or less")


@dataclass(frozen=True)
class BidStatusRevisionRepr:
    effective_date_from: str
    effective_date_to: str | None
    status: BidStatusRepr
    id: int | None = None

    @classmethod
    def from_domain(cls, bid_status_revision: BidStatusRevision) -> BidStatusRevisionRepr:
        return BidStatusRevisionRepr(
            id=bid_status_revision.id,
            effective_date_from=bid_status_revision.effective.date_from.isoformat(),
            effective_date_to=(
                bid_status_revision.effective.date_to.isoformat() if bid_status_revision.effective.date_to else None
            ),
            status=BidStatusRepr.from_domain(bid_status_revision.status),
        )

    def to_domain(self) -> BidStatusRevision:
        return BidStatusRevision(
            id_=self.id,
            effective=DateRange(
                date_from=datetime.fromisoformat(self.effective_date_from),
                date_to=datetime.fromisoformat(self.effective_date_to) if self.effective_date_to else None,
            ),
            status=self.status.to_domain(),
        )


@unique
class BidStatusRepr(Enum):
    SUBMITTED = "submitted"
    FUNDED = "funded"
    NOT_FUNDED = "not funded"
    SPLIT = "split"
    DELETED = "deleted"

    @classmethod
    def from_domain(cls, bid_status: BidStatus) -> BidStatusRepr:
        return cls._members()[bid_status]

    def to_domain(self) -> BidStatus:
        return inverse_dict(self._members())[self]

    @staticmethod
    def _members() -> dict[BidStatus, BidStatusRepr]:
        return {
            BidStatus.SUBMITTED: BidStatusRepr.SUBMITTED,
            BidStatus.FUNDED: BidStatusRepr.FUNDED,
            BidStatus.NOT_FUNDED: BidStatusRepr.NOT_FUNDED,
            BidStatus.SPLIT: BidStatusRepr.SPLIT,
            BidStatus.DELETED: BidStatusRepr.DELETED,
        }


@dataclass(frozen=True)
class FinancialRevisionRepr:
    effective_date_from: str
    effective_date_to: str | None
    type: FinancialTypeRepr
    amount: int
    source: DataSourceRepr
    id: int | None = None

    @classmethod
    def from_domain(cls, financial_revision: FinancialRevision) -> FinancialRevisionRepr:
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
