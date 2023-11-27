from schemes.domain.authorities import Authority, AuthorityRepository
from schemes.domain.schemes import Scheme, SchemeRepository
from schemes.domain.users import User, UserRepository


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


class MemoryUserRepository(UserRepository):
    def __init__(self) -> None:
        self._users: list[User] = []

    def add(self, *users: User) -> None:
        self._users.extend(users)

    def clear(self) -> None:
        self._users.clear()

    def get_by_email(self, email: str) -> User | None:
        return next((user for user in self._users if user.email == email), None)


class MemorySchemeRepository(SchemeRepository):
    def __init__(self) -> None:
        self._schemes: dict[int, Scheme] = {}

    def add(self, *schemes: Scheme) -> None:
        for scheme in schemes:
            self._schemes[scheme.id] = scheme

    def clear(self) -> None:
        self._schemes.clear()

    def get(self, id_: int) -> Scheme | None:
        return self._schemes[id_]

    def get_by_authority(self, authority_id: int) -> list[Scheme]:
        return sorted(
            [scheme for scheme in self._schemes.values() if scheme.authority_id == authority_id],
            key=lambda scheme: scheme.id,
        )

    def get_all(self) -> list[Scheme]:
        return sorted(list(self._schemes.values()), key=lambda scheme: scheme.id)
