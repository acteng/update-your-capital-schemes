class User:
    def __init__(self, email: str, authority_id: int):
        self.email = email
        self.authority_id = authority_id


class UserRepository:
    def add(self, *users: User) -> None:
        raise NotImplementedError()

    def clear(self) -> None:
        raise NotImplementedError()

    def get_by_email(self, email: str) -> User | None:
        raise NotImplementedError()
