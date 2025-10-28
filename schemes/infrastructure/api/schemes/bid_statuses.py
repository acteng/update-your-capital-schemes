from datetime import datetime
from enum import Enum

from schemes.domain.dates import DateRange
from schemes.domain.schemes.funding import BidStatus, BidStatusRevision
from schemes.infrastructure.api.base import BaseModel


class BidStatusModel(str, Enum):
    SUBMITTED = "submitted"
    FUNDED = "funded"
    NOT_FUNDED = "not funded"
    SPLIT = "split"
    DELETED = "deleted"

    def to_domain(self) -> BidStatus:
        return BidStatus[self.name]


class CapitalSchemeBidStatusDetailsModel(BaseModel):
    bid_status: BidStatusModel

    def to_domain(self) -> BidStatusRevision:
        # TODO: id, effective
        return BidStatusRevision(
            id_=0, effective=DateRange(date_from=datetime.min, date_to=None), status=self.bid_status.to_domain()
        )
