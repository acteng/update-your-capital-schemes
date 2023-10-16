from dataclasses import dataclass
from typing import List

import inject
from sqlalchemy import Column, Engine, MetaData, Table, Text, text


@dataclass
class User:
    email: str


class UserRepository:
    def add(self, user: User) -> None:
        raise NotImplementedError()

    def clear(self) -> None:
        raise NotImplementedError()

    def get(self, email: str) -> User | None:
        raise NotImplementedError()

    def get_all(self) -> List[User]:
        raise NotImplementedError()


def add_tables(metadata: MetaData) -> None:
    Table("users", metadata, Column("email", Text, nullable=False, unique=True))


class DatabaseUserRepository(UserRepository):
    @inject.autoparams()
    def __init__(self, engine: Engine):
        self._engine = engine

    def add(self, user: User) -> None:
        with self._engine.begin() as connection:
            connection.execute(text("INSERT INTO users (email) VALUES (:email)"), {"email": user.email})

    def clear(self) -> None:
        with self._engine.begin() as connection:
            connection.execute(text("DELETE FROM users"))

    def get(self, email: str) -> User | None:
        with self._engine.connect() as connection:
            result = connection.execute(text("SELECT email FROM users WHERE email = :email"), {"email": email})
            row = result.one_or_none()
            return User(row.email) if row else None

    def get_all(self) -> List[User]:
        with self._engine.connect() as connection:
            result = connection.execute(text("SELECT email FROM users"))
            return [User(row.email) for row in result]
