from typing import Generator

import pytest
from sqlalchemy import Engine, MetaData

from schemes.authorities.domain import Authority
from schemes.authorities.services import DatabaseAuthorityRepository
from schemes.authorities.services import add_tables as authorities_add_tables


@pytest.fixture(name="engine")
def engine_fixture(engine: Engine) -> Generator[Engine, None, None]:
    metadata = MetaData()
    authorities_add_tables(metadata)
    metadata.create_all(engine)
    yield engine


@pytest.fixture(name="authorities")
def authorities_fixture(engine: Engine) -> DatabaseAuthorityRepository:
    repository: DatabaseAuthorityRepository = DatabaseAuthorityRepository(engine)
    return repository


def test_add_authorities(authorities: DatabaseAuthorityRepository) -> None:
    authorities.add(
        Authority(id=1, name="Liverpool City Region Combined Authority"),
        Authority(id=2, name="West Yorkshire Combined Authority"),
    )

    assert authorities.get_all() == [
        Authority(id=1, name="Liverpool City Region Combined Authority"),
        Authority(id=2, name="West Yorkshire Combined Authority"),
    ]


def test_get_authority(authorities: DatabaseAuthorityRepository) -> None:
    authorities.add(
        Authority(id=1, name="Liverpool City Region Combined Authority"),
    )

    assert authorities.get(1) == Authority(id=1, name="Liverpool City Region Combined Authority")


def test_get_authority_that_does_not_exist(authorities: DatabaseAuthorityRepository) -> None:
    authorities.add(
        Authority(id=1, name="Liverpool City Region Combined Authority"),
    )

    assert authorities.get(2) is None


def test_get_all_authorities(authorities: DatabaseAuthorityRepository) -> None:
    authorities.add(
        Authority(id=1, name="Liverpool City Region Combined Authority"),
        Authority(id=2, name="West Yorkshire Combined Authority"),
    )

    authorities_list = authorities.get_all()

    assert authorities_list == [
        Authority(id=1, name="Liverpool City Region Combined Authority"),
        Authority(id=2, name="West Yorkshire Combined Authority"),
    ]


def test_clear_all_authorities(authorities: DatabaseAuthorityRepository) -> None:
    authorities.add(
        Authority(id=1, name="Liverpool City Region Combined Authority"),
        Authority(id=2, name="West Yorkshire Combined Authority"),
    )

    authorities.clear()

    assert authorities.get_all() == []
