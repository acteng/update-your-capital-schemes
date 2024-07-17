from datetime import datetime

from schemes.domain.dates import DateRange
from schemes.domain.schemes import (
    BidStatus,
    BidStatusRevision,
    FundingProgramme,
    FundingProgrammes,
    OverviewRevision,
    Scheme,
    SchemeType,
)


def build_scheme(
    id_: int,
    name: str | None = None,
    authority_id: int | None = None,
    type_: SchemeType | None = None,
    funding_programme: FundingProgramme = FundingProgrammes.ATF2,
    overview_revisions: list[OverviewRevision] | None = None,
    bid_status: BidStatus = BidStatus.FUNDED,
    bid_status_revisions: list[BidStatusRevision] | None = None,
) -> Scheme:
    if any((name is not None, authority_id is not None, type_ is not None)) == (overview_revisions is not None):
        assert False, "Either overview fields or revisions must be specified"

    if overview_revisions is not None:
        overview_revisions = overview_revisions
    elif name is not None and authority_id is not None:
        overview_revisions = [
            OverviewRevision(
                id_=None,
                effective=DateRange(datetime.min, None),
                name=name,
                authority_id=authority_id,
                type_=type_ or SchemeType.CONSTRUCTION,
            )
        ]
    else:
        assert False, "Overview fields must be specified"

    bid_status_revisions = (
        bid_status_revisions
        if bid_status_revisions is not None
        else [BidStatusRevision(id_=None, effective=DateRange(datetime.min, None), status=bid_status)]
    )

    scheme = Scheme(id_, funding_programme)
    scheme.overview.update_overviews(*overview_revisions)
    scheme.funding.update_bid_statuses(*bid_status_revisions)
    return scheme
