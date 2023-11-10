from typing import Generator

import pytest
from sqlalchemy import Engine, MetaData

from schemes.authorities.domain import Authority
from schemes.authorities.services import DatabaseAuthorityRepository
from schemes.authorities.services import add_tables as authorities_add_tables
from schemes.schemes.domain import Scheme, SchemeType
from schemes.schemes.services import DatabaseSchemeRepository
from schemes.schemes.services import add_tables as schemes_add_tables


@pytest.fixture(name="engine")
def engine_fixture(engine: Engine) -> Generator[Engine, None, None]:
    metadata = MetaData()
    authorities_add_tables(metadata)
    schemes_add_tables(metadata)
    metadata.create_all(engine)
    yield engine


@pytest.fixture(name="authorities")
def authorities_fixture(engine: Engine) -> DatabaseAuthorityRepository:
    repository: DatabaseAuthorityRepository = DatabaseAuthorityRepository(engine)
    return repository


@pytest.fixture(name="schemes")
def schemes_fixture(engine: Engine) -> DatabaseSchemeRepository:
    repository: DatabaseSchemeRepository = DatabaseSchemeRepository(engine)
    return repository


@pytest.fixture(name="authority", autouse=True)
def authority_fixture(authorities: DatabaseAuthorityRepository) -> None:
    authorities.add(
        Authority(id_=1, name="Liverpool City Region Combined Authority"),
        Authority(id_=2, name="West Yorkshire Combined Authority"),
    )


def test_add_schemes(schemes: DatabaseSchemeRepository) -> None:
    schemes.add(wirral_package(), school_streets())

    assert [_to_tuple(scheme) for scheme in schemes.get_all()] == [
        _to_tuple(wirral_package()),
        _to_tuple(school_streets()),
    ]


def test_get_scheme(schemes: DatabaseSchemeRepository) -> None:
    schemes.add(wirral_package())

    assert _to_tuple(schemes.get(1)) == _to_tuple(wirral_package())


def test_get_scheme_that_does_not_exist(schemes: DatabaseSchemeRepository) -> None:
    schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

    assert schemes.get(2) is None


def test_get_all_schemes_by_authority(schemes: DatabaseSchemeRepository) -> None:
    schemes.add(school_streets(), wirral_package(), Scheme(id_=3, name="Hospital Fields Road", authority_id=2))

    schemes_list = schemes.get_by_authority(1)

    assert [_to_tuple(scheme) for scheme in schemes_list] == [_to_tuple(wirral_package()), _to_tuple(school_streets())]


def test_get_all_schemes(schemes: DatabaseSchemeRepository) -> None:
    schemes.add(school_streets(), wirral_package())

    schemes_list = schemes.get_all()

    assert [_to_tuple(scheme) for scheme in schemes_list] == [_to_tuple(wirral_package()), _to_tuple(school_streets())]


def test_clear_all_schemes(schemes: DatabaseSchemeRepository) -> None:
    schemes.add(
        Scheme(id_=1, name="Wirral Package", authority_id=1),
        Scheme(id_=2, name="School Streets", authority_id=1),
    )

    schemes.clear()

    assert schemes.get_all() == []


def wirral_package() -> Scheme:
    scheme1 = Scheme(id_=1, name="Wirral Package", authority_id=1)
    scheme1.type = SchemeType.DEVELOPMENT
    return scheme1


def school_streets() -> Scheme:
    scheme2 = Scheme(id_=2, name="School Streets", authority_id=1)
    scheme2.type = SchemeType.CONSTRUCTION
    return scheme2


def _to_tuple(scheme: Scheme | None) -> tuple[int, str, int, SchemeType | None] | None:
    return (scheme.id, scheme.name, scheme.authority_id, scheme.type) if scheme else None
