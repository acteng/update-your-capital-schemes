import pytest
from sqlalchemy import MetaData, create_engine

from schemes.users import DatabaseUserRepository, User, add_tables


@pytest.fixture(name="users")
def users_fixture() -> DatabaseUserRepository:
    metadata = MetaData()
    add_tables(metadata)

    engine = create_engine("sqlite+pysqlite:///:memory:")
    metadata.create_all(engine)

    repository: DatabaseUserRepository = DatabaseUserRepository(engine)
    return repository


def test_add_users(users: DatabaseUserRepository) -> None:
    users.add(User("boardman@example.com"), User("obree@example.com"))

    assert users.get_all() == [User("boardman@example.com"), User("obree@example.com")]


def test_get_user_by_email(users: DatabaseUserRepository) -> None:
    users.add(User("boardman@example.com"))

    assert users.get_by_email("boardman@example.com") == User("boardman@example.com")


def test_get_user_by_email_who_does_not_exist(users: DatabaseUserRepository) -> None:
    users.add(User("boardman@example.com"))

    assert users.get_by_email("obree@example.com") is None


def test_get_all_users(users: DatabaseUserRepository) -> None:
    users.add(User("boardman@example.com"))
    users.add(User("obree@example.com"))

    user_list = users.get_all()

    assert user_list == [User("boardman@example.com"), User("obree@example.com")]


def test_clear_all_users(users: DatabaseUserRepository) -> None:
    users.add(User("boardman@example.com"))
    users.add(User("obree@example.com"))

    users.clear()

    assert users.get_all() == []
