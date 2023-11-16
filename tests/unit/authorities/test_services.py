import pytest
from sqlalchemy import Engine, MetaData

from schemes.authorities.domain import Authority
from schemes.authorities.services import DatabaseAuthorityRepository
from schemes.authorities.services import add_tables as authorities_add_tables


@pytest.fixture(name="engine")
def engine_fixture(engine: Engine) -> Engine:
    metadata = MetaData()
    authorities_add_tables(metadata)
    metadata.create_all(engine)
    return engine


@pytest.fixture(name="authorities")
def authorities_fixture(engine: Engine) -> DatabaseAuthorityRepository:
    repository: DatabaseAuthorityRepository = DatabaseAuthorityRepository(engine)
    return repository


def test_add_authorities(authorities: DatabaseAuthorityRepository) -> None:
    authorities.add(
        Authority(id_=1, name="Liverpool City Region Combined Authority"),
        Authority(id_=2, name="West Yorkshire Combined Authority"),
    )

    authority1: Authority
    authority2: Authority
    authority1, authority2 = authorities.get_all()

    assert authority1.id == 1 and authority1.name == "Liverpool City Region Combined Authority"
    assert authority2.id == 2 and authority2.name == "West Yorkshire Combined Authority"


def test_get_authority(authorities: DatabaseAuthorityRepository) -> None:
    authorities.add(
        Authority(id_=1, name="Liverpool City Region Combined Authority"),
    )

    authority = authorities.get(1)

    assert authority and authority.id == 1 and authority.name == "Liverpool City Region Combined Authority"


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

    authority1: Authority
    authority2: Authority
    authority1, authority2 = authorities.get_all()

    assert authority1.id == 1 and authority1.name == "Liverpool City Region Combined Authority"
    assert authority2.id == 2 and authority2.name == "West Yorkshire Combined Authority"


def test_clear_all_authorities(authorities: DatabaseAuthorityRepository) -> None:
    authorities.add(
        Authority(id_=1, name="Liverpool City Region Combined Authority"),
        Authority(id_=2, name="West Yorkshire Combined Authority"),
    )

    authorities.clear()

    assert authorities.get_all() == []
