import pytest
from sqlalchemy import Engine, MetaData, insert, select

from schemes.domain.authorities import Authority
from schemes.domain.users import User
from schemes.infrastructure.authorities import DatabaseAuthorityRepository
from schemes.infrastructure.authorities import add_tables as authorities_add_tables
from schemes.infrastructure.users import DatabaseUserRepository
from schemes.infrastructure.users import add_tables as users_add_tables


class TestDatabaseUserRepository:
    @pytest.fixture(name="metadata")
    def metadata_fixture(self) -> MetaData:
        metadata = MetaData()
        authorities_add_tables(metadata)
        users_add_tables(metadata)
        return metadata

    @pytest.fixture(name="engine")
    def engine_fixture(self, engine: Engine, metadata: MetaData) -> Engine:
        metadata.create_all(engine)
        return engine

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

    def test_add_users(self, users: DatabaseUserRepository, engine: Engine, metadata: MetaData) -> None:
        users.add(User(email="boardman@example.com", authority_id=1), User(email="obree@example.com", authority_id=1))

        user_table = metadata.tables["user"]
        with engine.connect() as connection:
            row1, row2 = connection.execute(select(user_table).order_by(user_table.c.user_id))
        assert row1.email == "boardman@example.com" and row1.authority_id == 1
        assert row2.email == "obree@example.com" and row2.authority_id == 1

    def test_get_user_by_email(self, users: DatabaseUserRepository, engine: Engine, metadata: MetaData) -> None:
        with engine.begin() as connection:
            connection.execute(insert(metadata.tables["user"]).values(email="boardman@example.com", authority_id=1))

        user = users.get_by_email("boardman@example.com")

        assert user and user.email == "boardman@example.com" and user.authority_id == 1

    def test_get_user_by_email_who_does_not_exist(
        self, users: DatabaseUserRepository, engine: Engine, metadata: MetaData
    ) -> None:
        with engine.begin() as connection:
            connection.execute(insert(metadata.tables["user"]).values(email="boardman@example.com", authority_id=1))

        assert users.get_by_email("obree@example.com") is None

    def test_clear_all_users(self, users: DatabaseUserRepository, engine: Engine, metadata: MetaData) -> None:
        user_table = metadata.tables["user"]
        with engine.begin() as connection:
            connection.execute(insert(user_table).values(email="boardman@example.com", authority_id=1))
            connection.execute(insert(user_table).values(email="obree@example.com", authority_id=1))

        users.clear()

        assert not users.get_by_email("boardman@example.com")
        assert not users.get_by_email("obree@example.com")