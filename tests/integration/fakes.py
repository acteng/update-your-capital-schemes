from typing import Dict, List, TypeGuard

from schemes.authorities.domain import Authority
from schemes.authorities.services import AuthorityRepository
from schemes.users.domain import User
from schemes.users.services import UserRepository


class MemoryAuthorityRepository(AuthorityRepository):
    def __init__(self) -> None:
        self._authorities: Dict[int, Authority] = {}

    def add(self, *authorities: Authority) -> None:
        for authority in authorities:
            self._authorities[authority.id] = authority

    def clear(self) -> None:
        self._authorities.clear()

    def get(self, id_: int) -> Authority | None:
        return self._authorities.get(id_)

    def get_all(self) -> List[Authority]:
        return list(self._authorities.values())


class MemoryUserRepository(UserRepository):
    def __init__(self) -> None:
        self._users: List[User] = []

    def add(self, *users: User) -> None:
        self._users.extend(users)

    def clear(self) -> None:
        self._users.clear()

    def get_by_email(self, email: str) -> User | None:
        def by_email(user: User) -> TypeGuard[User]:
            return user.email == email

        return next(filter(by_email, self._users), None)

    def get_all(self) -> List[User]:
        return self._users
