from dataclasses import dataclass


@dataclass(frozen=True)
class FundingProgramme:
    code: str
    is_eligible_for_authority_update: bool


class FundingProgrammes:
    ATF2 = FundingProgramme("ATF2", True)
    ATF3 = FundingProgramme("ATF3", True)
    ATF4 = FundingProgramme("ATF4", True)
    ATF4E = FundingProgramme("ATF4e", True)
    ATF5 = FundingProgramme("ATF5", True)
    CATF = FundingProgramme("CATF", True)
    CRSTS = FundingProgramme("CRSTS", False)
    IST = FundingProgramme("IST", True)
    LUF1 = FundingProgramme("LUF1", False)
    LUF2 = FundingProgramme("LUF2", False)
    LUF3 = FundingProgramme("LUF3", False)
    MRN = FundingProgramme("MRN", False)
    OTH = FundingProgramme("OTH", False)
    CON = FundingProgramme("CON", True)
    NCN = FundingProgramme("NCN", True)
    BUS = FundingProgramme("BUS", True)


class SchemeOverview:
    def __init__(self, name: str, authority_abbreviation: str, funding_programme: FundingProgramme):
        self._name = name
        self._authority_abbreviation = authority_abbreviation
        self._funding_programme = funding_programme

    @property
    def name(self) -> str:
        return self._name

    @property
    def authority_abbreviation(self) -> str:
        return self._authority_abbreviation

    @property
    def funding_programme(self) -> FundingProgramme:
        return self._funding_programme
