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
        Authority(id_=1, name="Liverpool City Region Combined Authority"),
        Authority(id_=2, name="West Yorkshire Combined Authority"),
    )

    assert [authority.__dict__ for authority in authorities.get_all()] == [
        Authority(id_=1, name="Liverpool City Region Combined Authority").__dict__,
        Authority(id_=2, name="West Yorkshire Combined Authority").__dict__,
    ]


def test_get_authority(authorities: DatabaseAuthorityRepository) -> None:
    authorities.add(
        Authority(id_=1, name="Liverpool City Region Combined Authority"),
    )

    assert authorities.get(1).__dict__ == Authority(id_=1, name="Liverpool City Region Combined Authority").__dict__


def test_get_authority_that_does_not_exist(authorities: DatabaseAuthorityRepository) -> None:
    authorities.add(
        Authority(id_=1, name="Liverpool City Region Combined Authority"),
    )

    assert authorities.get(2) is None


def test_get_all_authorities(authorities: DatabaseAuthorityRepository) -> None:
    authorities.add(
        Authority(id_=1, name="Liverpool City Region Combined Authority"),
        Authority(id_=2, name="West Yorkshire Combined Authority"),
    )

    authorities_list = authorities.get_all()

    assert [authority.__dict__ for authority in authorities_list] == [
        Authority(id_=1, name="Liverpool City Region Combined Authority").__dict__,
        Authority(id_=2, name="West Yorkshire Combined Authority").__dict__,
    ]


def test_clear_all_authorities(authorities: DatabaseAuthorityRepository) -> None:
    authorities.add(
        Authority(id_=1, name="Liverpool City Region Combined Authority"),
        Authority(id_=2, name="West Yorkshire Combined Authority"),
    )

    authorities.clear()

    assert authorities.get_all() == []
