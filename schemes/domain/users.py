class User:
    def __init__(self, email: str, authority_id: int):
        self._email = email
        self._authority_id = authority_id

    @property
    def email(self) -> str:
        return self._email

    @property
    def authority_id(self) -> int:
        return self._authority_id


class UserRepository:
    def add(self, *users: User) -> None:
        raise NotImplementedError()

    def clear(self) -> None:
        raise NotImplementedError()

    def get_by_email(self, email: str) -> User | None:
        raise NotImplementedError()
