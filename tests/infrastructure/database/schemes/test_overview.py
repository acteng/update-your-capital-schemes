import pytest

from schemes.domain.schemes import FundingProgramme, FundingProgrammes, SchemeType
from schemes.infrastructure.database.schemes.overview import FundingProgrammeMapper, SchemeTypeMapper


@pytest.mark.parametrize("type_, id_", [(SchemeType.DEVELOPMENT, 1), (SchemeType.CONSTRUCTION, 2)])
class TestSchemeTypeMapper:
    def test_to_id(self, type_: SchemeType, id_: int) -> None:
        assert SchemeTypeMapper().to_id(type_) == id_

    def test_to_domain(self, type_: SchemeType, id_: int) -> None:
        assert SchemeTypeMapper().to_domain(id_) == type_


@pytest.mark.parametrize(
    "funding_programme, id_",
    [
        (FundingProgrammes.ATF2, 1),
        (FundingProgrammes.ATF3, 2),
        (FundingProgrammes.ATF4, 3),
        (FundingProgrammes.ATF4E, 4),
        (FundingProgrammes.CRSTS, 5),
        (FundingProgrammes.LUF1, 6),
        (FundingProgrammes.LUF2, 7),
        (FundingProgrammes.LUF3, 8),
        (FundingProgrammes.MRN, 9),
        (FundingProgrammes.ATF5, 10),
    ],
)
class TestFundingProgrammeMapper:
    def test_to_id(self, funding_programme: FundingProgramme, id_: int) -> None:
        assert FundingProgrammeMapper().to_id(funding_programme) == id_

    def test_to_domain(self, funding_programme: FundingProgramme, id_: int) -> None:
        assert FundingProgrammeMapper().to_domain(id_) == funding_programme
