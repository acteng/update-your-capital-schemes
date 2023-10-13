import pytest

from schemes.users import DatabaseUserRepository, User


@pytest.fixture(name="users")
def users_fixture() -> DatabaseUserRepository:
    return DatabaseUserRepository()


def test_add_user(users: DatabaseUserRepository) -> None:
    users.add(User("boardman@example.com"))

    assert users.get("boardman@example.com") == User("boardman@example.com")


def test_get_user(users: DatabaseUserRepository) -> None:
    users.add(User("boardman@example.com"))

    assert users.get("boardman@example.com") == User("boardman@example.com")


def test_get_user_who_does_not_exist(users: DatabaseUserRepository) -> None:
    users.add(User("boardman@example.com"))

    assert users.get("obree@example.com") is None


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
