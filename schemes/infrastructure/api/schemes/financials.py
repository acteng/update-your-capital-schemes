from datetime import datetime
from typing import Self

from schemes.domain.dates import DateRange
from schemes.domain.schemes.funding import FinancialRevision
from schemes.infrastructure.api.base import BaseModel
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

    def to_domain(self) -> FinancialRevision:
        # TODO: id, effective
        return FinancialRevision(
            id_=0,
            effective=DateRange(date_from=datetime.min, date_to=None),
            type_=self.type.to_domain(),
            amount=self.amount,
            source=self.source.to_domain(),
        )
