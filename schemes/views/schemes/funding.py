from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Self

from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovTextInput
from wtforms.validators import InputRequired, NumberRange, ValidationError

from schemes.domain.schemes.funding import SchemeFunding
from schemes.domain.schemes.schemes import Scheme
from schemes.views.forms import CustomMessageIntegerField


@dataclass(frozen=True)
class SchemeFundingContext:
    funding_allocation: int | None
    spend_to_date: int | None
    allocation_still_to_spend: int

    @classmethod
    def from_domain(cls, funding: SchemeFunding) -> Self:
        return cls(
            funding_allocation=funding.funding_allocation,
            spend_to_date=funding.spend_to_date,
            allocation_still_to_spend=funding.allocation_still_to_spend,
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
    def from_domain(cls, funding: SchemeFunding) -> Self:
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
class ChangeSpendToDateContext:
    reference: str
    name: str
    funding_allocation: int | None
    form: ChangeSpendToDateForm

    @classmethod
    def from_domain(cls, scheme: Scheme) -> Self:
        name = scheme.overview.name
        assert name is not None

        return cls(
            reference=scheme.reference,
            name=name,
            funding_allocation=scheme.funding.funding_allocation,
            form=ChangeSpendToDateForm.from_domain(scheme.funding),
        )
