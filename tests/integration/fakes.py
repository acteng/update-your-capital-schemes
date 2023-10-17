from typing import List, TypeGuard

from schemes.users import User, UserRepository


class MemoryUserRepository(UserRepository):
    def __init__(self) -> None:
        self._users: List[User] = []

    def add(self, user: User) -> None:
        self._users.append(user)

    def clear(self) -> None:
        self._users.clear()

    def get_by_email(self, email: str) -> User | None:
        def by_email(user: User) -> TypeGuard[User]:
            return user.email == email

        return next(filter(by_email, self._users), None)

    def get_all(self) -> List[User]:
        return self._users
