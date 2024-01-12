import pytest
from sqlalchemy import Engine, insert, select

from schemes.domain.authorities import Authority
from schemes.domain.users import User
from schemes.infrastructure import user_table
from schemes.infrastructure.authorities import DatabaseAuthorityRepository
from schemes.infrastructure.users import DatabaseUserRepository


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

        with engine.connect() as connection:
            row1, row2 = connection.execute(select(user_table).order_by(user_table.c.user_id))
        assert row1.email == "boardman@example.com" and row1.authority_id == 1
        assert row2.email == "obree@example.com" and row2.authority_id == 1

    def test_get_user_by_email(self, users: DatabaseUserRepository, engine: Engine) -> None:
        with engine.begin() as connection:
            connection.execute(insert(user_table).values(email="boardman@example.com", authority_id=1))

        user = users.get_by_email("boardman@example.com")

        assert user and user.email == "boardman@example.com" and user.authority_id == 1

    def test_get_user_by_email_who_does_not_exist(self, users: DatabaseUserRepository, engine: Engine) -> None:
        with engine.begin() as connection:
            connection.execute(insert(user_table).values(email="boardman@example.com", authority_id=1))

        assert users.get_by_email("obree@example.com") is None

    def test_clear_all_users(self, users: DatabaseUserRepository, engine: Engine) -> None:
        with engine.begin() as connection:
            connection.execute(insert(user_table).values(email="boardman@example.com", authority_id=1))
            connection.execute(insert(user_table).values(email="obree@example.com", authority_id=1))

        users.clear()

        assert not users.get_by_email("boardman@example.com")
        assert not users.get_by_email("obree@example.com")
