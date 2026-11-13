from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import ClassVar, Self

from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovTextInput
from wtforms.validators import InputRequired, NumberRange, ValidationError

from schemes.domain.schemes.financials import FundingProgramme, FundingProgrammes, SchemeFinancials
from schemes.domain.schemes.schemes import Scheme
from schemes.views.forms import CustomMessageIntegerField


@dataclass(frozen=True)
class FundingProgrammeContext:
    name: str
    _NAMES: ClassVar[Mapping[FundingProgramme, str]] = {
        FundingProgrammes.ATF2: "ATF2",
        FundingProgrammes.ATF3: "ATF3",
        FundingProgrammes.ATF4: "ATF4",
        FundingProgrammes.ATF4E: "ATF4e",
        FundingProgrammes.ATF5: "ATF5",
        FundingProgrammes.CATF: "CATF",
        FundingProgrammes.CRSTS: "CRSTS",
        FundingProgrammes.IST: "IST",
        FundingProgrammes.LUF1: "LUF1",
        FundingProgrammes.LUF2: "LUF2",
        FundingProgrammes.LUF3: "LUF3",
        FundingProgrammes.MRN: "MRN",
        FundingProgrammes.OTH: "OTH",
        FundingProgrammes.CON: "CON",
        FundingProgrammes.NCN: "NCN",
        FundingProgrammes.BUS: "BUS",
    }

    @classmethod
    def from_domain(cls, funding_programme: FundingProgramme) -> Self:
        return cls(name=cls._NAMES[funding_programme])


@dataclass(frozen=True)
class SchemeFundingRowContext:
    funding_programme: FundingProgrammeContext
    amount: int


@dataclass(frozen=True)
class SchemeFundingContext:
    fundings: list[SchemeFundingRowContext]
    funding_allocation: int | None

    @classmethod
    def from_domain(cls, financials: SchemeFinancials) -> Self:
        return cls(
            fundings=[
                SchemeFundingRowContext(
                    funding_programme=FundingProgrammeContext.from_domain(funding.funding_programme),
                    amount=funding.amount,
                )
                for funding in financials.fundings
            ],
            funding_allocation=financials.funding_allocation,
        )


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
