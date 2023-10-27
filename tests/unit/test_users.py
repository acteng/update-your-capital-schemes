import pytest
from sqlalchemy import MetaData, create_engine

from schemes import authorities, users
from schemes.users import DatabaseUserRepository, User


@pytest.fixture(name="users")
def users_fixture() -> DatabaseUserRepository:
    metadata = MetaData()
    authorities.add_tables(metadata)
    users.add_tables(metadata)

    engine = create_engine("sqlite+pysqlite:///:memory:")
    metadata.create_all(engine)

    repository: DatabaseUserRepository = DatabaseUserRepository(engine)
    return repository


def test_add_users(users: DatabaseUserRepository) -> None:
    users.add(User(email="boardman@example.com", authority_id=1), User(email="obree@example.com", authority_id=1))

    assert users.get_all() == [
        User(email="boardman@example.com", authority_id=1),
        User(email="obree@example.com", authority_id=1),
    ]


def test_get_user_by_email(users: DatabaseUserRepository) -> None:
    users.add(User(email="boardman@example.com", authority_id=1))

    assert users.get_by_email("boardman@example.com") == User("boardman@example.com", authority_id=1)


def test_get_user_by_email_who_does_not_exist(users: DatabaseUserRepository) -> None:
    users.add(User(email="boardman@example.com", authority_id=1))

    assert users.get_by_email("obree@example.com") is None


def test_get_all_users(users: DatabaseUserRepository) -> None:
    users.add(User(email="boardman@example.com", authority_id=1), User(email="obree@example.com", authority_id=1))

    user_list = users.get_all()

    assert user_list == [
        User(email="boardman@example.com", authority_id=1),
        User(email="obree@example.com", authority_id=1),
    ]


def test_clear_all_users(users: DatabaseUserRepository) -> None:
    users.add(User(email="boardman@example.com", authority_id=1), User(email="obree@example.com", authority_id=1))

    users.clear()

    assert users.get_all() == []
