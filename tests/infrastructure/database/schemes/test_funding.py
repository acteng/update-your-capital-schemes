import pytest

from schemes.domain.schemes import BidStatus, FinancialType
from schemes.infrastructure.database.schemes.funding import BidStatusMapper, FinancialTypeMapper


@pytest.mark.parametrize(
    "bid_status, id_",
    [
        (BidStatus.SUBMITTED, 1),
        (BidStatus.FUNDED, 2),
        (BidStatus.NOT_FUNDED, 3),
        (BidStatus.SPLIT, 4),
        (BidStatus.DELETED, 5),
    ],
)
class TestBidStatusMapper:
    def test_to_id(self, bid_status: BidStatus, id_: int) -> None:
        assert BidStatusMapper().to_id(bid_status) == id_

    def test_to_domain(self, bid_status: BidStatus, id_: int) -> None:
        assert BidStatusMapper().to_domain(id_) == bid_status


@pytest.mark.parametrize(
    "financial_type, id_",
    [
        (FinancialType.EXPECTED_COST, 1),
        (FinancialType.ACTUAL_COST, 2),
        (FinancialType.FUNDING_ALLOCATION, 3),
        (FinancialType.SPEND_TO_DATE, 4),
        (FinancialType.FUNDING_REQUEST, 5),
    ],
)
class TestFinancialTypeMapper:
    def test_to_id(self, financial_type: FinancialType, id_: int) -> None:
        assert FinancialTypeMapper().to_id(financial_type) == id_

    def test_to_domain(self, financial_type: FinancialType, id_: int) -> None:
        assert FinancialTypeMapper().to_domain(id_) == financial_type
