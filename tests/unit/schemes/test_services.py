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
        Authority(id=1, name="Liverpool City Region Combined Authority"),
        Authority(id=2, name="West Yorkshire Combined Authority"),
    )


def test_add_schemes(schemes: DatabaseSchemeRepository) -> None:
    schemes.add(
        Scheme(id=1, name="Wirral Package", authority_id=1),
        Scheme(id=2, name="School Streets", authority_id=1),
    )

    assert schemes.get_all() == [
        Scheme(id=1, name="Wirral Package", authority_id=1),
        Scheme(id=2, name="School Streets", authority_id=1),
    ]


def test_get_all_schemes_by_authority(schemes: DatabaseSchemeRepository) -> None:
    schemes.add(
        Scheme(id=2, name="School Streets", authority_id=1),
        Scheme(id=1, name="Wirral Package", authority_id=1),
        Scheme(id=3, name="Hospital Fields Road", authority_id=2),
    )

    schemes_list = schemes.get_by_authority(1)

    assert schemes_list == [
        Scheme(id=1, name="Wirral Package", authority_id=1),
        Scheme(id=2, name="School Streets", authority_id=1),
    ]


def test_get_all_schemes(schemes: DatabaseSchemeRepository) -> None:
    schemes.add(
        Scheme(id=2, name="School Streets", authority_id=1),
        Scheme(id=1, name="Wirral Package", authority_id=1),
    )

    schemes_list = schemes.get_all()

    assert schemes_list == [
        Scheme(id=1, name="Wirral Package", authority_id=1),
        Scheme(id=2, name="School Streets", authority_id=1),
    ]


def test_clear_all_schemes(schemes: DatabaseSchemeRepository) -> None:
    schemes.add(
        Scheme(id=1, name="Wirral Package", authority_id=1),
        Scheme(id=2, name="School Streets", authority_id=1),
    )

    schemes.clear()

    assert schemes.get_all() == []
