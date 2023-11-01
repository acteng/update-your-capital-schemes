import pytest
from sqlalchemy import MetaData, create_engine

import schemes.authorities.services
from schemes.authorities.domain import Authority
from schemes.authorities.services import DatabaseAuthorityRepository


@pytest.fixture(name="authorities")
def authorities_fixture() -> DatabaseAuthorityRepository:
    metadata = MetaData()
    schemes.authorities.add_tables(metadata)

    engine = create_engine("sqlite+pysqlite:///:memory:")
    metadata.create_all(engine)

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
