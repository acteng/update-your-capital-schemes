import pytest
from sqlalchemy import Engine, MetaData

from schemes.authorities.domain import Authority
from schemes.authorities.services import DatabaseAuthorityRepository
from schemes.authorities.services import add_tables as authorities_add_tables
from schemes.users.domain import User
from schemes.users.services import DatabaseUserRepository
from schemes.users.services import add_tables as users_add_tables


@pytest.fixture(name="engine")
def engine_fixture(engine: Engine) -> Engine:
    metadata = MetaData()
    authorities_add_tables(metadata)
    users_add_tables(metadata)
    metadata.create_all(engine)
    return engine


@pytest.fixture(name="authorities")
def authorities_fixture(engine: Engine) -> DatabaseAuthorityRepository:
    repository: DatabaseAuthorityRepository = DatabaseAuthorityRepository(engine)
    return repository


@pytest.fixture(name="users")
def users_fixture(engine: Engine) -> DatabaseUserRepository:
    repository: DatabaseUserRepository = DatabaseUserRepository(engine)
    return repository


@pytest.fixture(name="authority", autouse=True)
def authority_fixture(authorities: DatabaseAuthorityRepository) -> None:
    authorities.add(Authority(id_=1, name="Liverpool City Region Combined Authority"))


def test_add_users(users: DatabaseUserRepository) -> None:
    users.add(User(email="boardman@example.com", authority_id=1), User(email="obree@example.com", authority_id=1))

    user1: User
    user2: User
    user1, user2 = users.get_all()

    assert user1.email == "boardman@example.com" and user1.authority_id == 1
    assert user2.email == "obree@example.com" and user2.authority_id == 1


def test_get_user_by_email(users: DatabaseUserRepository) -> None:
    users.add(User(email="boardman@example.com", authority_id=1))

    user = users.get_by_email("boardman@example.com")

    assert user and user.email == "boardman@example.com" and user.authority_id == 1


def test_get_user_by_email_who_does_not_exist(users: DatabaseUserRepository) -> None:
    users.add(User(email="boardman@example.com", authority_id=1))

    assert users.get_by_email("obree@example.com") is None


def test_get_all_users(users: DatabaseUserRepository) -> None:
    users.add(User(email="boardman@example.com", authority_id=1), User(email="obree@example.com", authority_id=1))

    user1: User
    user2: User
    user1, user2 = users.get_all()

    assert user1.email == "boardman@example.com" and user1.authority_id == 1
    assert user2.email == "obree@example.com" and user2.authority_id == 1


def test_clear_all_users(users: DatabaseUserRepository) -> None:
    users.add(User(email="boardman@example.com", authority_id=1), User(email="obree@example.com", authority_id=1))

    users.clear()

    assert users.get_all() == []
