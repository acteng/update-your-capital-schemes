import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from schemes.domain.authorities import Authority
from schemes.domain.users import User
from schemes.infrastructure.database import UserEntity
from schemes.infrastructure.database.authorities import DatabaseAuthorityRepository
from schemes.infrastructure.database.users import DatabaseUserRepository


class TestDatabaseUserRepository:
    @pytest.fixture(name="authorities")
    def authorities_fixture(self, session_maker: sessionmaker[Session]) -> DatabaseAuthorityRepository:
        repository: DatabaseAuthorityRepository = DatabaseAuthorityRepository(session_maker)
        return repository

    @pytest.fixture(name="users")
    def users_fixture(self, session_maker: sessionmaker[Session]) -> DatabaseUserRepository:
        repository: DatabaseUserRepository = DatabaseUserRepository(session_maker)
        return repository

    @pytest.fixture(name="authority", autouse=True)
    def authority_fixture(self, authorities: DatabaseAuthorityRepository) -> None:
        authorities.add(Authority(abbreviation="LIV", name="Liverpool City Region Combined Authority"))

    def test_add_users(self, users: DatabaseUserRepository, session_maker: sessionmaker[Session]) -> None:
        users.add(
            User(email="boardman@example.com", authority_abbreviation="LIV"),
            User(email="obree@example.com", authority_abbreviation="LIV"),
        )

        row1: UserEntity
        row2: UserEntity
        with session_maker() as session:
            row1, row2 = session.scalars(select(UserEntity).order_by(UserEntity.user_id))
        assert row1.email == "boardman@example.com" and row1.authority_abbreviation == "LIV"
        assert row2.email == "obree@example.com" and row2.authority_abbreviation == "LIV"

    def test_get_user(self, users: DatabaseUserRepository, session_maker: sessionmaker[Session]) -> None:
        with session_maker() as session:
            session.add(UserEntity(email="boardman@example.com", authority_abbreviation="LIV"))
            session.commit()

        user = users.get("boardman@example.com")

        assert user and user.email == "boardman@example.com" and user.authority_abbreviation == "LIV"

    def test_get_user_who_does_not_exist(
        self, users: DatabaseUserRepository, session_maker: sessionmaker[Session]
    ) -> None:
        with session_maker() as session:
            session.add(UserEntity(email="boardman@example.com", authority_abbreviation="LIV"))
            session.commit()

        assert users.get("obree@example.com") is None

    def test_clear_all_users(self, users: DatabaseUserRepository, session_maker: sessionmaker[Session]) -> None:
        with session_maker() as session:
            session.add_all(
                [
                    UserEntity(email="boardman@example.com", authority_abbreviation="LIV"),
                    UserEntity(email="obree@example.com", authority_abbreviation="LIV"),
                ]
            )
            session.commit()

        users.clear()

        with session_maker() as session:
            assert session.execute(select(func.count()).select_from(UserEntity)).scalar_one() == 0
