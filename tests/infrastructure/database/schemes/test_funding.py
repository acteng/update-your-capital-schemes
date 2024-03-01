import pytest

from schemes.domain.schemes import FinancialType
from schemes.infrastructure.database.schemes.funding import FinancialTypeMapper


@pytest.mark.parametrize(
    "financial_type, id_",
    [
        (FinancialType.EXPECTED_COST, 1),
        (FinancialType.ACTUAL_COST, 2),
        (FinancialType.FUNDING_ALLOCATION, 3),
        (FinancialType.SPENT_TO_DATE, 4),
        (FinancialType.FUNDING_REQUEST, 5),
    ],
)
class TestFinancialTypeMapper:
    def test_to_id(self, financial_type: FinancialType, id_: int) -> None:
        assert FinancialTypeMapper().to_id(financial_type) == id_

    def test_to_domain(self, financial_type: FinancialType, id_: int) -> None:
        assert FinancialTypeMapper().to_domain(id_) == financial_type
