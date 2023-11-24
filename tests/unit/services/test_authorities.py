import pytest
from sqlalchemy import Engine, MetaData, insert, select

from schemes.domain.authorities import Authority
from schemes.services.authorities import DatabaseAuthorityRepository
from schemes.services.authorities import add_tables as authorities_add_tables


@pytest.fixture(name="metadata")
def metadata_fixture() -> MetaData:
    metadata = MetaData()
    authorities_add_tables(metadata)
    return metadata


@pytest.fixture(name="engine")
def engine_fixture(engine: Engine, metadata: MetaData) -> Engine:
    metadata.create_all(engine)
    return engine


@pytest.fixture(name="authorities")
def authorities_fixture(engine: Engine) -> DatabaseAuthorityRepository:
    repository: DatabaseAuthorityRepository = DatabaseAuthorityRepository(engine)
    return repository


def test_add_authorities(authorities: DatabaseAuthorityRepository, engine: Engine, metadata: MetaData) -> None:
    authorities.add(
        Authority(id_=1, name="Liverpool City Region Combined Authority"),
        Authority(id_=2, name="West Yorkshire Combined Authority"),
    )

    authority_table = metadata.tables["authority"]
    with engine.connect() as connection:
        row1, row2 = connection.execute(select(authority_table).order_by(authority_table.c.authority_id))
    assert row1.authority_id == 1 and row1.authority_name == "Liverpool City Region Combined Authority"
    assert row2.authority_id == 2 and row2.authority_name == "West Yorkshire Combined Authority"


def test_get_authority(authorities: DatabaseAuthorityRepository, engine: Engine, metadata: MetaData) -> None:
    with engine.begin() as connection:
        connection.execute(
            insert(metadata.tables["authority"]).values(
                authority_id=1, authority_name="Liverpool City Region Combined Authority"
            )
        )

    authority = authorities.get(1)

    assert authority and authority.id == 1 and authority.name == "Liverpool City Region Combined Authority"


def test_get_authority_that_does_not_exist(
    authorities: DatabaseAuthorityRepository, engine: Engine, metadata: MetaData
) -> None:
    with engine.begin() as connection:
        connection.execute(
            insert(metadata.tables["authority"]).values(
                authority_id=1, authority_name="Liverpool City Region Combined Authority"
            )
        )

    assert authorities.get(2) is None


def test_get_all_authorities(authorities: DatabaseAuthorityRepository, engine: Engine, metadata: MetaData) -> None:
    authority_table = metadata.tables["authority"]
    with engine.begin() as connection:
        connection.execute(
            insert(authority_table).values(authority_id=1, authority_name="Liverpool City Region Combined Authority")
        )
        connection.execute(
            insert(authority_table).values(authority_id=2, authority_name="West Yorkshire Combined Authority")
        )

    authority1: Authority
    authority2: Authority
    authority1, authority2 = authorities.get_all()

    assert authority1.id == 1 and authority1.name == "Liverpool City Region Combined Authority"
    assert authority2.id == 2 and authority2.name == "West Yorkshire Combined Authority"


def test_clear_all_authorities(authorities: DatabaseAuthorityRepository, engine: Engine, metadata: MetaData) -> None:
    authority_table = metadata.tables["authority"]
    with engine.begin() as connection:
        connection.execute(
            insert(authority_table).values(authority_id=1, authority_name="Liverpool City Region Combined Authority")
        )
        connection.execute(
            insert(authority_table).values(authority_id=2, authority_name="West Yorkshire Combined Authority")
        )

    authorities.clear()

    assert authorities.get_all() == []
