class User:
    def __init__(self, email: str, authority_abbreviation: str):
        self._email = email
        self._authority_abbreviation = authority_abbreviation

    @property
    def email(self) -> str:
        return self._email

    @property
    def authority_abbreviation(self) -> str:
        return self._authority_abbreviation


class UserRepository:
    def add(self, *users: User) -> None:
        raise NotImplementedError()

    def clear(self) -> None:
        raise NotImplementedError()

    def get(self, email: str) -> User | None:
        raise NotImplementedError()
