from datetime import datetime
from enum import Enum

from schemes.domain.dates import DateRange
from schemes.domain.schemes.data_sources import DataSource
from schemes.domain.schemes.funding import FinancialRevision, FinancialType
from schemes.infrastructure.api.base import BaseModel


class FinancialTypeModel(str, Enum):
    EXPECTED_COST = "expected cost"
    ACTUAL_COST = "actual cost"
    FUNDING_ALLOCATION = "funding allocation"
    SPEND_TO_DATE = "spend to date"
    FUNDING_REQUEST = "funding request"

    def to_domain(self) -> FinancialType:
        return FinancialType[self.name]


class CapitalSchemeFinancialModel(BaseModel):
    type: FinancialTypeModel
    amount: int

    def to_domain(self) -> FinancialRevision:
        # TODO: id, effective, source
        return FinancialRevision(
            id_=None,
            effective=DateRange(date_from=datetime.min, date_to=None),
            type_=self.type.to_domain(),
            amount=self.amount,
            source=DataSource.PULSE_5,
        )
