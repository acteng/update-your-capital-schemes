from typing import Generator

import pytest
from sqlalchemy import Engine, MetaData

from schemes.authorities.domain import Authority
from schemes.authorities.services import DatabaseAuthorityRepository
from schemes.authorities.services import add_tables as authorities_add_tables
from schemes.schemes.domain import Scheme
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
    schemes.add(
        Scheme(id_=1, name="Wirral Package", authority_id=1),
        Scheme(id_=2, name="School Streets", authority_id=1),
    )

    assert [scheme.__dict__ for scheme in schemes.get_all()] == [
        Scheme(id_=1, name="Wirral Package", authority_id=1).__dict__,
        Scheme(id_=2, name="School Streets", authority_id=1).__dict__,
    ]


def test_get_scheme(schemes: DatabaseSchemeRepository) -> None:
    schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

    assert schemes.get(1).__dict__ == Scheme(id_=1, name="Wirral Package", authority_id=1).__dict__


def test_get_scheme_that_does_not_exist(schemes: DatabaseSchemeRepository) -> None:
    schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

    assert schemes.get(2) is None


def test_get_all_schemes_by_authority(schemes: DatabaseSchemeRepository) -> None:
    schemes.add(
        Scheme(id_=2, name="School Streets", authority_id=1),
        Scheme(id_=1, name="Wirral Package", authority_id=1),
        Scheme(id_=3, name="Hospital Fields Road", authority_id=2),
    )

    schemes_list = schemes.get_by_authority(1)

    assert [scheme.__dict__ for scheme in schemes_list] == [
        Scheme(id_=1, name="Wirral Package", authority_id=1).__dict__,
        Scheme(id_=2, name="School Streets", authority_id=1).__dict__,
    ]


def test_get_all_schemes(schemes: DatabaseSchemeRepository) -> None:
    schemes.add(
        Scheme(id_=2, name="School Streets", authority_id=1),
        Scheme(id_=1, name="Wirral Package", authority_id=1),
    )

    schemes_list = schemes.get_all()

    assert [scheme.__dict__ for scheme in schemes_list] == [
        Scheme(id_=1, name="Wirral Package", authority_id=1).__dict__,
        Scheme(id_=2, name="School Streets", authority_id=1).__dict__,
    ]


def test_clear_all_schemes(schemes: DatabaseSchemeRepository) -> None:
    schemes.add(
        Scheme(id_=1, name="Wirral Package", authority_id=1),
        Scheme(id_=2, name="School Streets", authority_id=1),
    )

    schemes.clear()

    assert schemes.get_all() == []
