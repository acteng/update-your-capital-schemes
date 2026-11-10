from __future__ import annotations

from dataclasses import dataclass
from typing import Self

from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovTextInput
from wtforms.validators import InputRequired, NumberRange, ValidationError

from schemes.domain.schemes.financials import SchemeFinancials
from schemes.domain.schemes.schemes import Scheme
from schemes.views.forms import CustomMessageIntegerField


@dataclass(frozen=True)
class SchemeFundingContext:
    funding_allocation: int | None

    @classmethod
    def from_domain(cls, financials: SchemeFinancials) -> Self:
        return cls(funding_allocation=financials.funding_allocation)


@dataclass(frozen=True)
class SchemeSpendContext:
    funding_allocation: int | None
    spend_to_date: int | None
    allocation_still_to_spend: int

    @classmethod
    def from_domain(cls, financials: SchemeFinancials) -> Self:
        return cls(
            funding_allocation=financials.funding_allocation,
            spend_to_date=financials.spend_to_date,
            allocation_still_to_spend=financials.allocation_still_to_spend,
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
    def from_domain(cls, financials: SchemeFinancials) -> Self:
        funding_allocation = financials.funding_allocation or 0
        return cls(max_amount=funding_allocation, data={"amount": financials.spend_to_date})

    def update_domain(self, financials: SchemeFinancials) -> None:
        assert self.amount.data is not None
        financials.update_spend_to_date(self.amount.data)

    @staticmethod
    def validate_amount(form: ChangeSpendToDateForm, field: CustomMessageIntegerField) -> None:
        if field.data is not None and field.data > form.max_amount:
            raise ValidationError(f"Spend to date must be £{form.max_amount:,} or less")


@dataclass(frozen=True)
class ChangeSpendToDateContext:
    reference: str
    name: str
    funding_allocation: int | None
    form: ChangeSpendToDateForm

    @classmethod
    def from_domain(cls, scheme: Scheme) -> Self:
        return cls(
            reference=scheme.reference,
            name=scheme.overview.name,
            funding_allocation=scheme.financials.funding_allocation,
            form=ChangeSpendToDateForm.from_domain(scheme.financials),
        )
