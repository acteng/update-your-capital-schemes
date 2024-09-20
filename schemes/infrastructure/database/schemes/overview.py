from schemes.dicts import inverse_dict
from schemes.domain.schemes import FundingProgramme, FundingProgrammes, SchemeType


class SchemeTypeMapper:
    _IDS = {
        SchemeType.DEVELOPMENT: 1,
        SchemeType.CONSTRUCTION: 2,
    }

    def to_id(self, type_: SchemeType) -> int:
        return self._IDS[type_]

    def to_domain(self, id_: int) -> SchemeType:
        return inverse_dict(self._IDS)[id_]


class FundingProgrammeMapper:
    _IDS = {
        FundingProgrammes.ATF2: 1,
        FundingProgrammes.ATF3: 2,
        FundingProgrammes.ATF4: 3,
        FundingProgrammes.ATF4E: 4,
        FundingProgrammes.CRSTS: 5,
        FundingProgrammes.LUF1: 6,
        FundingProgrammes.LUF2: 7,
        FundingProgrammes.LUF3: 8,
    }

    def to_id(self, funding_programme: FundingProgramme) -> int:
        return self._IDS[funding_programme]

    def to_domain(self, id_: int) -> FundingProgramme:
        return inverse_dict(self._IDS)[id_]
