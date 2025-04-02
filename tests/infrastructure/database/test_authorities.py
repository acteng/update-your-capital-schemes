import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from schemes.domain.authorities import Authority
from schemes.infrastructure.database import AuthorityEntity
from schemes.infrastructure.database.authorities import DatabaseAuthorityRepository


class TestDatabaseAuthorityRepository:
    @pytest.fixture(name="authorities")
    def authorities_fixture(self, session_maker: sessionmaker[Session]) -> DatabaseAuthorityRepository:
        repository: DatabaseAuthorityRepository = DatabaseAuthorityRepository(session_maker)
        return repository

    def test_add_authorities(
        self, authorities: DatabaseAuthorityRepository, session_maker: sessionmaker[Session]
    ) -> None:
        authorities.add(
            Authority(abbreviation="LIV", name="Liverpool City Region Combined Authority"),
            Authority(abbreviation="WYO", name="West Yorkshire Combined Authority"),
        )

        row1: AuthorityEntity
        row2: AuthorityEntity
        with session_maker() as session:
            row1, row2 = session.scalars(select(AuthorityEntity).order_by(AuthorityEntity.authority_id))
        assert row1.authority_id == 1 and row1.authority_full_name == "Liverpool City Region Combined Authority"
        assert row2.authority_id == 2 and row2.authority_full_name == "West Yorkshire Combined Authority"

    def test_get_authority(
        self, authorities: DatabaseAuthorityRepository, session_maker: sessionmaker[Session]
    ) -> None:
        with session_maker() as session:
            session.add(
                AuthorityEntity(
                    authority_abbreviation="LIV", authority_full_name="Liverpool City Region Combined Authority"
                )
            )
            session.commit()

        authority = authorities.get("LIV")

        assert (
            authority
            and authority.abbreviation == "LIV"
            and authority.name == "Liverpool City Region Combined Authority"
        )

    def test_get_authority_that_does_not_exist(
        self, authorities: DatabaseAuthorityRepository, session_maker: sessionmaker[Session]
    ) -> None:
        with session_maker() as session:
            session.add(
                AuthorityEntity(
                    authority_abbreviation="LIV", authority_full_name="Liverpool City Region Combined Authority"
                )
            )
            session.commit()

        assert authorities.get("WYO") is None

    def test_clear_all_authorities(
        self, authorities: DatabaseAuthorityRepository, session_maker: sessionmaker[Session]
    ) -> None:
        with session_maker() as session:
            session.add_all(
                [
                    AuthorityEntity(
                        authority_abbreviation="LIV", authority_full_name="Liverpool City Region Combined Authority"
                    ),
                    AuthorityEntity(
                        authority_abbreviation="WYO", authority_full_name="West Yorkshire Combined Authority"
                    ),
                ]
            )
            session.commit()

        authorities.clear()

        with session_maker() as session:
            assert session.execute(select(func.count()).select_from(AuthorityEntity)).scalar_one() == 0
