from typing import TypeGuard

from schemes.authorities.domain import Authority
from schemes.authorities.services import AuthorityRepository
from schemes.schemes.domain import Scheme
from schemes.schemes.services import SchemeRepository
from schemes.users.domain import User
from schemes.users.services import UserRepository


class MemoryAuthorityRepository(AuthorityRepository):
    def __init__(self) -> None:
        self._authorities: dict[int, Authority] = {}

    def add(self, *authorities: Authority) -> None:
        for authority in authorities:
            self._authorities[authority.id] = authority

    def clear(self) -> None:
        self._authorities.clear()

    def get(self, id_: int) -> Authority | None:
        return self._authorities.get(id_)

    def get_all(self) -> list[Authority]:
        return list(self._authorities.values())


class MemoryUserRepository(UserRepository):
    def __init__(self) -> None:
        self._users: list[User] = []

    def add(self, *users: User) -> None:
        self._users.extend(users)

    def clear(self) -> None:
        self._users.clear()

    def get_by_email(self, email: str) -> User | None:
        def by_email(user: User) -> TypeGuard[User]:
            return user.email == email

        return next(filter(by_email, self._users), None)

    def get_all(self) -> list[User]:
        return self._users


class MemorySchemeRepository(SchemeRepository):
    def __init__(self) -> None:
        self._schemes: dict[int, Scheme] = {}

    def add(self, *schemes: Scheme) -> None:
        for scheme in schemes:
            self._schemes[scheme.id] = scheme

    def clear(self) -> None:
        self._schemes.clear()

    def get_by_authority(self, authority_id: int) -> list[Scheme]:
        def by_authority(scheme: Scheme) -> TypeGuard[Scheme]:
            return scheme.authority_id == authority_id

        return list(filter(by_authority, self._schemes.values()))

    def get_all(self) -> list[Scheme]:
        return list(self._schemes.values())
