from enum import Enum
from typing import Self

from schemes.domain.schemes.funding import FinancialType


class FinancialTypeModel(str, Enum):
    EXPECTED_COST = "expected cost"
    ACTUAL_COST = "actual cost"
    FUNDING_ALLOCATION = "funding allocation"
    SPEND_TO_DATE = "spend to date"
    FUNDING_REQUEST = "funding request"

    @classmethod
    def from_domain(cls, type_: FinancialType) -> Self:
        return cls[type_.name]

    def to_domain(self) -> FinancialType:
        return FinancialType[self.name]
