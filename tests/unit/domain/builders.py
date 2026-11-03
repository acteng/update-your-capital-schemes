from schemes.domain.schemes.overview import FundingProgramme, FundingProgrammes, OverviewRevision
from schemes.domain.schemes.schemes import Scheme, Status


class _Unset:
    pass


_UNSET = _Unset()


def build_scheme(
    reference: str,
    name: str | None = None,
    authority_abbreviation: str | None = None,
    funding_programme: FundingProgramme | None = None,
    overview_revision: OverviewRevision | None | _Unset = _UNSET,
    status: Status = Status.ACTIVE,
) -> Scheme:
    if any((name is not None, authority_abbreviation is not None, funding_programme is not None)) == (
        not isinstance(overview_revision, _Unset)
    ):
        assert False, "Either overview fields or revision must be specified"

    if not isinstance(overview_revision, _Unset):
        pass
    elif name is not None:
        overview_revision = OverviewRevision(
            name=name,
            authority_abbreviation=authority_abbreviation or "",
            funding_programme=funding_programme or FundingProgrammes.ATF2,
        )
    else:
        assert False, "Overview fields must be specified"

    scheme = Scheme(reference, status)
    if overview_revision:
        scheme.overview.update_overview(overview_revision)
    return scheme
