from datetime import datetime
from typing import Self

from schemes.domain.dates import DateRange
from schemes.domain.schemes.funding import FinancialRevision, FinancialType
from schemes.infrastructure.api.base import BaseModel
from schemes.infrastructure.api.collections import CollectionModel
from schemes.infrastructure.api.data_sources import DataSourceModel
from schemes.infrastructure.api.financial_types import FinancialTypeModel


class CapitalSchemeFinancialModel(BaseModel):
    type: FinancialTypeModel
    amount: int
    source: DataSourceModel

    @classmethod
    def from_domain(cls, financial_revision: FinancialRevision) -> Self:
        return cls(
            type=FinancialTypeModel.from_domain(financial_revision.type),
            amount=financial_revision.amount,
            source=DataSourceModel.from_domain(financial_revision.source),
        )


class CapitalSchemeFundingModel(BaseModel):
    amount: int
    source: DataSourceModel

    def to_domain(self) -> FinancialRevision:
        # TODO: id, effective
        return FinancialRevision(
            id_=0,
            effective=DateRange(date_from=datetime.min, date_to=None),
            type_=FinancialType.FUNDING_ALLOCATION,
            amount=self.amount,
            source=self.source.to_domain(),
        )


class CapitalSchemeSpendModel(BaseModel):
    amount: int
    source: DataSourceModel

    def to_domain(self) -> FinancialRevision:
        # TODO: id, effective
        return FinancialRevision(
            id_=0,
            effective=DateRange(date_from=datetime.min, date_to=None),
            type_=FinancialType.SPEND_TO_DATE,
            amount=self.amount,
            source=self.source.to_domain(),
        )


class CapitalSchemeFinancialsModel(BaseModel):
    funding: CollectionModel[CapitalSchemeFundingModel]
    spend: CapitalSchemeSpendModel | None

    def to_domain(self) -> list[FinancialRevision]:
        financial_revisions = [funding.to_domain() for funding in self.funding.items]
        if self.spend:
            financial_revisions.append(self.spend.to_domain())
        return financial_revisions
