import pytest
from sqlalchemy import Engine, insert, select

from schemes.domain.authorities import Authority
from schemes.infrastructure import authority_table
from schemes.infrastructure.authorities import DatabaseAuthorityRepository


class TestDatabaseAuthorityRepository:
    @pytest.fixture(name="authorities")
    def authorities_fixture(self, engine: Engine) -> DatabaseAuthorityRepository:
        repository: DatabaseAuthorityRepository = DatabaseAuthorityRepository(engine)
        return repository

    def test_add_authorities(self, authorities: DatabaseAuthorityRepository, engine: Engine) -> None:
        authorities.add(
            Authority(id_=1, name="Liverpool City Region Combined Authority"),
            Authority(id_=2, name="West Yorkshire Combined Authority"),
        )

        with engine.connect() as connection:
            row1, row2 = connection.execute(select(authority_table).order_by(authority_table.c.authority_id))
        assert row1.authority_id == 1 and row1.authority_name == "Liverpool City Region Combined Authority"
        assert row2.authority_id == 2 and row2.authority_name == "West Yorkshire Combined Authority"

    def test_get_authority(self, authorities: DatabaseAuthorityRepository, engine: Engine) -> None:
        with engine.begin() as connection:
            connection.execute(
                insert(authority_table).values(
                    authority_id=1, authority_name="Liverpool City Region Combined Authority"
                )
            )

        authority = authorities.get(1)

        assert authority and authority.id == 1 and authority.name == "Liverpool City Region Combined Authority"

    def test_get_authority_that_does_not_exist(self, authorities: DatabaseAuthorityRepository, engine: Engine) -> None:
        with engine.begin() as connection:
            connection.execute(
                insert(authority_table).values(
                    authority_id=1, authority_name="Liverpool City Region Combined Authority"
                )
            )

        assert authorities.get(2) is None

    def test_clear_all_authorities(self, authorities: DatabaseAuthorityRepository, engine: Engine) -> None:
        with engine.begin() as connection:
            connection.execute(
                insert(authority_table).values(
                    authority_id=1, authority_name="Liverpool City Region Combined Authority"
                )
            )
            connection.execute(
                insert(authority_table).values(authority_id=2, authority_name="West Yorkshire Combined Authority")
            )

        authorities.clear()

        assert not authorities.get(1)
