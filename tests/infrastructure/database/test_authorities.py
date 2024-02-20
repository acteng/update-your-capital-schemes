import pytest
from sqlalchemy import Engine, func, select
from sqlalchemy.orm import Session

from schemes.domain.authorities import Authority
from schemes.infrastructure.database import AuthorityEntity
from schemes.infrastructure.database.authorities import DatabaseAuthorityRepository


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

        row1: AuthorityEntity
        row2: AuthorityEntity
        with Session(engine) as session:
            row1, row2 = session.scalars(select(AuthorityEntity).order_by(AuthorityEntity.authority_id))
        assert row1.authority_id == 1 and row1.authority_name == "Liverpool City Region Combined Authority"
        assert row2.authority_id == 2 and row2.authority_name == "West Yorkshire Combined Authority"

    def test_get_authority(self, authorities: DatabaseAuthorityRepository, engine: Engine) -> None:
        with Session(engine) as session:
            session.add(AuthorityEntity(authority_id=1, authority_name="Liverpool City Region Combined Authority"))
            session.commit()

        authority = authorities.get(1)

        assert authority and authority.id == 1 and authority.name == "Liverpool City Region Combined Authority"

    def test_get_authority_that_does_not_exist(self, authorities: DatabaseAuthorityRepository, engine: Engine) -> None:
        with Session(engine) as session:
            session.add(AuthorityEntity(authority_id=1, authority_name="Liverpool City Region Combined Authority"))
            session.commit()

        assert authorities.get(2) is None

    def test_clear_all_authorities(self, authorities: DatabaseAuthorityRepository, engine: Engine) -> None:
        with Session(engine) as session:
            session.add_all(
                [
                    AuthorityEntity(authority_id=1, authority_name="Liverpool City Region Combined Authority"),
                    AuthorityEntity(authority_id=2, authority_name="West Yorkshire Combined Authority"),
                ]
            )
            session.commit()

        authorities.clear()

        with Session(engine) as session:
            assert session.execute(select(func.count()).select_from(AuthorityEntity)).scalar_one() == 0
