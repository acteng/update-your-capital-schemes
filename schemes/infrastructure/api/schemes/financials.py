from typing import Self

from schemes.domain.schemes.funding import FinancialType, SchemeFinancial
from schemes.infrastructure.api.base import BaseModel
from schemes.infrastructure.api.collections import CollectionModel
from schemes.infrastructure.api.data_sources import DataSourceModel


class CapitalSchemeFundingModel(BaseModel):
    amount: int
    source: DataSourceModel

    def to_domain(self) -> SchemeFinancial:
        # TODO: id
        return SchemeFinancial(
            id_=0, type_=FinancialType.FUNDING_ALLOCATION, amount=self.amount, source=self.source.to_domain()
        )


class CapitalSchemeSpendModel(BaseModel):
    amount: int
    source: DataSourceModel

    @classmethod
    def from_domain(cls, financial: SchemeFinancial) -> Self:
        if financial.type != FinancialType.SPEND_TO_DATE:
            raise ValueError(f"Invalid financial type: {financial.type}")

        return cls(amount=financial.amount, source=DataSourceModel.from_domain(financial.source))

    def to_domain(self) -> SchemeFinancial:
        # TODO: id
        return SchemeFinancial(
            id_=0,
            type_=FinancialType.SPEND_TO_DATE,
            amount=self.amount,
            source=self.source.to_domain(),
        )


class CapitalSchemeFinancialsModel(BaseModel):
    funding: CollectionModel[CapitalSchemeFundingModel]
    spend: CapitalSchemeSpendModel | None

    def to_domain(self) -> list[SchemeFinancial]:
        financials = [funding.to_domain() for funding in self.funding.items]
        if self.spend:
            financials.append(self.spend.to_domain())
        return financials
