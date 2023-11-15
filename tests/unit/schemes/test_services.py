from typing import Generator

import pytest
from sqlalchemy import Engine, MetaData

from schemes.authorities.domain import Authority
from schemes.authorities.services import DatabaseAuthorityRepository
from schemes.authorities.services import add_tables as authorities_add_tables
from schemes.schemes.domain import FundingProgramme, Scheme, SchemeType
from schemes.schemes.services import (
    DatabaseSchemeRepository,
    FundingProgrammeMapper,
    SchemeTypeMapper,
)
from schemes.schemes.services import add_tables as schemes_add_tables


class TestDatabaseSchemeRepository:
    @pytest.fixture(name="engine")
    def engine_fixture(self, engine: Engine) -> Generator[Engine, None, None]:
        metadata = MetaData()
        authorities_add_tables(metadata)
        schemes_add_tables(metadata)
        metadata.create_all(engine)
        yield engine

    @pytest.fixture(name="authorities")
    def authorities_fixture(self, engine: Engine) -> DatabaseAuthorityRepository:
        repository: DatabaseAuthorityRepository = DatabaseAuthorityRepository(engine)
        return repository

    @pytest.fixture(name="schemes")
    def schemes_fixture(self, engine: Engine) -> DatabaseSchemeRepository:
        repository: DatabaseSchemeRepository = DatabaseSchemeRepository(engine)
        return repository

    @pytest.fixture(name="authority", autouse=True)
    def authority_fixture(self, authorities: DatabaseAuthorityRepository) -> None:
        authorities.add(
            Authority(id_=1, name="Liverpool City Region Combined Authority"),
            Authority(id_=2, name="West Yorkshire Combined Authority"),
        )

    def test_add_schemes(self, schemes: DatabaseSchemeRepository) -> None:
        scheme1 = Scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme1.type = SchemeType.DEVELOPMENT
        scheme1.funding_programme = FundingProgramme.ATF3
        schemes.add(scheme1, Scheme(id_=2, name="School Streets", authority_id=1))

        actual1: Scheme
        actual2: Scheme
        actual1, actual2 = schemes.get_all()

        assert (
            actual1.id == 1
            and actual1.name == "Wirral Package"
            and actual1.authority_id == 1
            and actual1.type == SchemeType.DEVELOPMENT
            and actual1.funding_programme == FundingProgramme.ATF3
        )
        assert actual2.id == 2 and actual2.name == "School Streets" and actual1.authority_id == 1

    def test_get_scheme(self, schemes: DatabaseSchemeRepository) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme.type = SchemeType.DEVELOPMENT
        scheme.funding_programme = FundingProgramme.ATF3
        schemes.add(scheme)

        actual = schemes.get(1)

        assert (
            actual
            and actual.id == 1
            and actual.name == "Wirral Package"
            and actual.authority_id == 1
            and actual.type == SchemeType.DEVELOPMENT
            and actual.funding_programme == FundingProgramme.ATF3
        )

    def test_get_scheme_that_does_not_exist(self, schemes: DatabaseSchemeRepository) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        assert schemes.get(2) is None

    def test_get_all_schemes_by_authority(self, schemes: DatabaseSchemeRepository) -> None:
        scheme1 = Scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme1.type = SchemeType.DEVELOPMENT
        scheme1.funding_programme = FundingProgramme.ATF3
        schemes.add(
            scheme1,
            Scheme(id_=2, name="School Streets", authority_id=1),
            Scheme(id_=3, name="Hospital Fields Road", authority_id=2),
        )

        actual1: Scheme
        actual2: Scheme
        actual1, actual2 = schemes.get_by_authority(1)

        assert (
            actual1.id == 1
            and actual1.name == "Wirral Package"
            and actual1.authority_id == 1
            and actual1.type == SchemeType.DEVELOPMENT
            and actual1.funding_programme == FundingProgramme.ATF3
        )
        assert actual2.id == 2 and actual2.name == "School Streets" and actual1.authority_id == 1

    def test_get_all_schemes(self, schemes: DatabaseSchemeRepository) -> None:
        scheme1 = Scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme1.type = SchemeType.DEVELOPMENT
        scheme1.funding_programme = FundingProgramme.ATF3
        schemes.add(scheme1, Scheme(id_=2, name="School Streets", authority_id=1))

        actual1: Scheme
        actual2: Scheme
        actual1, actual2 = schemes.get_all()

        assert (
            actual1.id == 1
            and actual1.name == "Wirral Package"
            and actual1.authority_id == 1
            and actual1.type == SchemeType.DEVELOPMENT
            and actual1.funding_programme == FundingProgramme.ATF3
        )
        assert actual2.id == 2 and actual2.name == "School Streets" and actual1.authority_id == 1

    def test_clear_all_schemes(self, schemes: DatabaseSchemeRepository) -> None:
        schemes.add(
            Scheme(id_=1, name="Wirral Package", authority_id=1),
            Scheme(id_=2, name="School Streets", authority_id=1),
        )

        schemes.clear()

        assert schemes.get_all() == []


class TestSchemeTypeMapper:
    @pytest.mark.parametrize("type_, id_", [(SchemeType.DEVELOPMENT, 1), (SchemeType.CONSTRUCTION, 2), (None, None)])
    def test_mapper(self, type_: SchemeType | None, id_: int | None) -> None:
        mapper = SchemeTypeMapper()
        assert mapper.to_id(type_) == id_ and mapper.to_domain(id_) == type_


class TestFundingProgrammeMapper:
    @pytest.mark.parametrize(
        "funding_programme, id_",
        [
            (FundingProgramme.ATF2, 1),
            (FundingProgramme.ATF3, 2),
            (FundingProgramme.ATF4, 3),
            (FundingProgramme.ATF4E, 4),
            (FundingProgramme.ATF5, 5),
            (FundingProgramme.MRN, 6),
            (FundingProgramme.LUF, 7),
            (FundingProgramme.CRSTS, 8),
            (None, None),
        ],
    )
    def test_mapper(self, funding_programme: FundingProgramme | None, id_: int | None) -> None:
        mapper = FundingProgrammeMapper()
        assert mapper.to_id(funding_programme) == id_ and mapper.to_domain(id_) == funding_programme
