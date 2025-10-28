import pytest

from schemes.domain.schemes.funding import BidStatus
from schemes.infrastructure.api.schemes.bid_statuses import BidStatusModel, CapitalSchemeBidStatusDetailsModel


class TestBidStatusModel:
    @pytest.mark.parametrize(
        "bid_status_model, expected_bid_status",
        [
            (BidStatusModel.SUBMITTED, BidStatus.SUBMITTED),
            (BidStatusModel.FUNDED, BidStatus.FUNDED),
            (BidStatusModel.NOT_FUNDED, BidStatus.NOT_FUNDED),
            (BidStatusModel.SPLIT, BidStatus.SPLIT),
            (BidStatusModel.DELETED, BidStatus.DELETED),
        ],
    )
    def test_to_domain(self, bid_status_model: BidStatusModel, expected_bid_status: BidStatus) -> None:
        assert bid_status_model.to_domain() == expected_bid_status


class TestCapitalSchemeBidStatusDetailsModel:
    def test_to_domain(self) -> None:
        bid_status_details_model = CapitalSchemeBidStatusDetailsModel(bid_status=BidStatusModel.FUNDED)

        bid_status_revision = bid_status_details_model.to_domain()

        assert bid_status_revision.id is not None and bid_status_revision.status == BidStatus.FUNDED
