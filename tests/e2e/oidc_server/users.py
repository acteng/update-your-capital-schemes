from dataclasses import dataclass


@dataclass
class StubUser:
    id: str
    email: str


class UserRepository:
    def __init__(self) -> None:
        self._users: dict[str, StubUser] = {}

    def add(self, user: StubUser) -> None:
        self._users[user.id] = user

    def get(self, user_id: str) -> StubUser:
        return self._users[user_id]

    def clear(self) -> None:
        self._users.clear()
