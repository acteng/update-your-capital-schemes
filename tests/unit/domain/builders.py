from schemes.domain.schemes.data_sources import DataSource
from schemes.domain.schemes.financials import SchemeFunding
from schemes.domain.schemes.overview import FundingProgramme, FundingProgrammes, SchemeOverview
from schemes.domain.schemes.schemes import Scheme, Status


def build_scheme(
    reference: str,
    name: str | None = None,
    authority_abbreviation: str | None = None,
    overview: SchemeOverview | None = None,
    status: Status = Status.ACTIVE,
) -> Scheme:
    if any((name is not None, authority_abbreviation is not None)) == (overview is not None):
        assert False, "Either overview fields or overview must be specified"

    if overview is not None:
        pass
    elif name is not None:
        overview = SchemeOverview(name=name, authority_abbreviation=authority_abbreviation or "")
    else:
        assert False, "Overview fields must be specified"

    return Scheme(reference, overview, status)


def build_scheme_funding(
    funding_programme: FundingProgramme | None = None, amount: int = 0, source: DataSource | None = None
) -> SchemeFunding:
    return SchemeFunding(
        funding_programme=funding_programme or FundingProgrammes.ATF2,
        amount=amount,
        source=source or DataSource.PULSE_5,
    )
