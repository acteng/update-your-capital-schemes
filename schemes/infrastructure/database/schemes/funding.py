from schemes.dicts import inverse_dict
from schemes.domain.schemes import FinancialType


class FinancialTypeMapper:
    _IDS = {
        FinancialType.EXPECTED_COST: 1,
        FinancialType.ACTUAL_COST: 2,
        FinancialType.FUNDING_ALLOCATION: 3,
        FinancialType.SPENT_TO_DATE: 4,
        FinancialType.FUNDING_REQUEST: 5,
    }

    def to_id(self, financial_type: FinancialType) -> int:
        return self._IDS[financial_type]

    def to_domain(self, id_: int) -> FinancialType:
        return inverse_dict(self._IDS)[id_]
