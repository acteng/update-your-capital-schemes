from typing import Self

from schemes.domain.schemes.financials import SchemeFunding, SchemeSpend
from schemes.infrastructure.api.base import BaseModel
from schemes.infrastructure.api.collections import CollectionModel
from schemes.infrastructure.api.data_sources import DataSourceModel


class CapitalSchemeFundingModel(BaseModel):
    amount: int
    source: DataSourceModel

    def to_domain(self) -> SchemeFunding:
        return SchemeFunding(amount=self.amount, source=self.source.to_domain())


class CapitalSchemeSpendModel(BaseModel):
    amount: int
    source: DataSourceModel

    @classmethod
    def from_domain(cls, spend: SchemeSpend) -> Self:
        return cls(amount=spend.amount, source=DataSourceModel.from_domain(spend.source))

    def to_domain(self) -> SchemeSpend:
        # TODO: id
        return SchemeSpend(id_=0, amount=self.amount, source=self.source.to_domain())


class CapitalSchemeFinancialsModel(BaseModel):
    funding: CollectionModel[CapitalSchemeFundingModel]
    spend: CapitalSchemeSpendModel | None

    def to_funding_domain(self) -> list[SchemeFunding]:
        return [funding.to_domain() for funding in self.funding.items]

    def to_spend_domain(self) -> SchemeSpend | None:
        return self.spend.to_domain() if self.spend else None
