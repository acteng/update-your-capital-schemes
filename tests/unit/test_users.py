import pytest

from schemes.users import User, UserRepository


@pytest.fixture(name="user_repository")
def user_repository_fixture() -> UserRepository:
    return UserRepository()


def test_add_user(user_repository: UserRepository) -> None:
    user_repository.add(User("boardman@example.com"))

    assert user_repository.get("boardman@example.com") == User("boardman@example.com")


def test_get_user(user_repository: UserRepository) -> None:
    user_repository.add(User("boardman@example.com"))

    assert user_repository.get("boardman@example.com") == User("boardman@example.com")


def test_get_user_who_does_not_exist(user_repository: UserRepository) -> None:
    user_repository.add(User("boardman@example.com"))

    assert user_repository.get("obree@example.com") is None


def test_get_all_users(user_repository: UserRepository) -> None:
    user_repository.add(User("boardman@example.com"))
    user_repository.add(User("obree@example.com"))

    user_list = user_repository.get_all()

    assert user_list == [User("boardman@example.com"), User("obree@example.com")]


def test_clear_all_users(user_repository: UserRepository) -> None:
    user_repository.add(User("boardman@example.com"))
    user_repository.add(User("obree@example.com"))

    user_repository.clear()

    assert user_repository.get_all() == []
