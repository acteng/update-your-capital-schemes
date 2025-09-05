from copy import deepcopy

from schemes.domain.authorities import Authority, AuthorityRepository
from schemes.domain.schemes.schemes import Scheme, SchemeRepository
from schemes.domain.users import User, UserRepository


class MemoryAuthorityRepository(AuthorityRepository):
    def __init__(self) -> None:
        self._authorities: dict[str, Authority] = {}

    async def add(self, *authorities: Authority) -> None:
        for authority in authorities:
            self._authorities[authority.abbreviation] = authority

    async def clear(self) -> None:
        self._authorities.clear()

    async def get(self, abbreviation: str) -> Authority | None:
        return self._authorities.get(abbreviation)


class MemoryUserRepository(UserRepository):
    def __init__(self) -> None:
        self._users: list[User] = []

    def add(self, *users: User) -> None:
        self._users.extend(users)

    def clear(self) -> None:
        self._users.clear()

    def get(self, email: str) -> User | None:
        return next((user for user in self._users if user.email == email), None)


class MemorySchemeRepository(SchemeRepository):
    def __init__(self) -> None:
        self._schemes: dict[str, Scheme] = {}

    async def add(self, *schemes: Scheme) -> None:
        for scheme in schemes:
            self._schemes[scheme.reference] = scheme

    async def clear(self) -> None:
        self._schemes.clear()

    async def get(self, reference: str) -> Scheme | None:
        return deepcopy(self._schemes.get(reference))

    async def get_by_authority(self, authority_abbreviation: str) -> list[Scheme]:
        return sorted(
            [
                deepcopy(scheme)
                for scheme in self._schemes.values()
                if scheme.overview.authority_abbreviation == authority_abbreviation
            ],
            key=lambda scheme: scheme.id,
        )

    async def update(self, scheme: Scheme) -> None:
        self._schemes[scheme.reference] = scheme
