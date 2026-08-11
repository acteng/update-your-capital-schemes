from datetime import datetime

from schemes.domain.dates import DateRange
from schemes.domain.schemes.overview import FundingProgramme, FundingProgrammes, OverviewRevision, SchemeType
from schemes.domain.schemes.schemes import Scheme, Status


def build_scheme(
    reference: str,
    name: str | None = None,
    authority_abbreviation: str | None = None,
    type_: SchemeType | None = None,
    funding_programme: FundingProgramme | None = None,
    overview_revisions: list[OverviewRevision] | None = None,
    status: Status = Status.ACTIVE,
) -> Scheme:
    if any(
        (name is not None, authority_abbreviation is not None, type_ is not None, funding_programme is not None)
    ) == (overview_revisions is not None):
        assert False, "Either overview fields or revisions must be specified"

    if overview_revisions is not None:
        pass
    elif name is not None:
        overview_revisions = [
            OverviewRevision(
                effective=DateRange(datetime.min, None),
                name=name,
                authority_abbreviation=authority_abbreviation or "",
                type_=type_ or SchemeType.CONSTRUCTION,
                funding_programme=funding_programme or FundingProgrammes.ATF2,
            )
        ]
    else:
        assert False, "Overview fields must be specified"

    scheme = Scheme(reference, status)
    scheme.overview.update_overviews(*overview_revisions)
    return scheme
