from schemes.domain.schemes.overview import FundingProgramme, FundingProgrammes, OverviewRevision
from schemes.domain.schemes.schemes import Scheme, Status


def build_scheme(
    reference: str,
    name: str | None = None,
    authority_abbreviation: str | None = None,
    funding_programme: FundingProgramme | None = None,
    overview_revision: OverviewRevision | None = None,
    status: Status = Status.ACTIVE,
) -> Scheme:
    if any((name is not None, authority_abbreviation is not None, funding_programme is not None)) == (
        overview_revision is not None
    ):
        assert False, "Either overview fields or revision must be specified"

    if overview_revision is not None:
        pass
    elif name is not None:
        overview_revision = OverviewRevision(
            name=name,
            authority_abbreviation=authority_abbreviation or "",
            funding_programme=funding_programme or FundingProgrammes.ATF2,
        )
    else:
        assert False, "Overview fields must be specified"

    return Scheme(reference, overview_revision, status)
