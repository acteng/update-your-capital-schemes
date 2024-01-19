import pytest
from sqlalchemy import Engine, func, select
from sqlalchemy.orm import Session

from schemes.domain.authorities import Authority
from schemes.domain.users import User
from schemes.infrastructure.database import UserEntity
from schemes.infrastructure.database.authorities import DatabaseAuthorityRepository
from schemes.infrastructure.database.users import DatabaseUserRepository


class TestDatabaseUserRepository:
    @pytest.fixture(name="authorities")
    def authorities_fixture(self, engine: Engine) -> DatabaseAuthorityRepository:
        repository: DatabaseAuthorityRepository = DatabaseAuthorityRepository(engine)
        return repository

    @pytest.fixture(name="users")
    def users_fixture(self, engine: Engine) -> DatabaseUserRepository:
        repository: DatabaseUserRepository = DatabaseUserRepository(engine)
        return repository

    @pytest.fixture(name="authority", autouse=True)
    def authority_fixture(self, authorities: DatabaseAuthorityRepository) -> None:
        authorities.add(Authority(id_=1, name="Liverpool City Region Combined Authority"))

    def test_add_users(self, users: DatabaseUserRepository, engine: Engine) -> None:
        users.add(User(email="boardman@example.com", authority_id=1), User(email="obree@example.com", authority_id=1))

        with Session(engine) as session:
            row1, row2 = session.scalars(select(UserEntity).order_by(UserEntity.user_id))
        assert row1.email == "boardman@example.com" and row1.authority_id == 1
        assert row2.email == "obree@example.com" and row2.authority_id == 1

    def test_get_user_by_email(self, users: DatabaseUserRepository, engine: Engine) -> None:
        with Session(engine) as session:
            session.add(UserEntity(email="boardman@example.com", authority_id=1))
            session.commit()

        user = users.get_by_email("boardman@example.com")

        assert user and user.email == "boardman@example.com" and user.authority_id == 1

    def test_get_user_by_email_who_does_not_exist(self, users: DatabaseUserRepository, engine: Engine) -> None:
        with Session(engine) as session:
            session.add(UserEntity(email="boardman@example.com", authority_id=1))
            session.commit()

        assert users.get_by_email("obree@example.com") is None

    def test_clear_all_users(self, users: DatabaseUserRepository, engine: Engine) -> None:
        with Session(engine) as session:
            session.add_all(
                [
                    UserEntity(email="boardman@example.com", authority_id=1),
                    UserEntity(email="obree@example.com", authority_id=1),
                ]
            )
            session.commit()

        users.clear()

        with Session(engine) as session:
            assert session.execute(select(func.count()).select_from(UserEntity)).scalar_one() == 0
