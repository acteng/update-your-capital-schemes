from datetime import datetime

from schemes.domain.dates import DateRange
from schemes.domain.schemes import BidStatus, BidStatusRevision, Scheme


def build_scheme(id_: int, name: str, authority_id: int, bid_status: BidStatus = BidStatus.FUNDED) -> Scheme:
    scheme = Scheme(id_, name, authority_id)
    scheme.funding.update_bid_statuses(
        BidStatusRevision(id_=None, effective=DateRange(datetime.min, None), status=bid_status)
    )
    return scheme
