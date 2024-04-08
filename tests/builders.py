from datetime import datetime

from schemes.domain.dates import DateRange
from schemes.domain.schemes import BidStatus, BidStatusRevision, Scheme, SchemeType


def build_scheme(
    id_: int,
    name: str,
    authority_id: int,
    type_: SchemeType = SchemeType.CONSTRUCTION,
    bid_status: BidStatus = BidStatus.FUNDED,
    bid_status_revisions: list[BidStatusRevision] | None = None,
) -> Scheme:
    bid_status_revisions = (
        bid_status_revisions
        if bid_status_revisions is not None
        else [BidStatusRevision(id_=None, effective=DateRange(datetime.min, None), status=bid_status)]
    )

    scheme = Scheme(id_, name, authority_id, type_)
    scheme.funding.update_bid_statuses(*bid_status_revisions)
    return scheme
