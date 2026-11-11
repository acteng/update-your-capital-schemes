from schemes.domain.schemes.financials import SchemeFunding
from schemes.domain.schemes.overview import FundingProgramme, FundingProgrammes, SchemeOverview
from schemes.domain.schemes.schemes import Scheme, Status


def build_scheme(
    reference: str = "dummy", overview: SchemeOverview | None = None, status: Status = Status.ACTIVE
) -> Scheme:
    return Scheme(reference, overview or build_scheme_overview(), status)


def build_scheme_overview(name: str = "dummy", authority_abbreviation: str = "dummy") -> SchemeOverview:
    return SchemeOverview(name=name, authority_abbreviation=authority_abbreviation)


def build_scheme_funding(
    funding_programme: FundingProgramme = FundingProgrammes.ATF2, amount: int = 0
) -> SchemeFunding:
    return SchemeFunding(funding_programme=funding_programme, amount=amount)
