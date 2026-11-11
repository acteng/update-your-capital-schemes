from typing import Self

from pydantic import AnyUrl

from schemes.domain.schemes.financials import SchemeFunding, SchemeSpend
from schemes.infrastructure.api.base import BaseModel
from schemes.infrastructure.api.collections import CollectionModel
from schemes.infrastructure.api.data_sources import DataSourceModel
from schemes.infrastructure.api.funding_programmes import FundingProgrammeModel


class CapitalSchemeFundingModel(BaseModel):
    funding_programme: AnyUrl
    amount: int

    def to_domain(self, funding_programme_models: list[FundingProgrammeModel]) -> SchemeFunding:
        return SchemeFunding(
            funding_programme=next(
                funding_programme_model.to_domain()
                for funding_programme_model in funding_programme_models
                if funding_programme_model.id == self.funding_programme
            ),
            amount=self.amount,
        )


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

    def to_funding_domain(self, funding_programme_models: list[FundingProgrammeModel]) -> list[SchemeFunding]:
        return [funding.to_domain(funding_programme_models) for funding in self.funding.items]

    def to_spend_domain(self) -> SchemeSpend | None:
        return self.spend.to_domain() if self.spend else None
