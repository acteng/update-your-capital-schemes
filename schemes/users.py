from dataclasses import dataclass
from typing import List

import inject
from flask import Blueprint, Response, request
from sqlalchemy import Column, Engine, Integer, MetaData, String, Table, text

from schemes.api_key_auth import api_key_auth


@dataclass
class User:
    email: str


class UserRepository:
    def add(self, *users: User) -> None:
        raise NotImplementedError()

    def clear(self) -> None:
        raise NotImplementedError()

    def get_by_email(self, email: str) -> User | None:
        raise NotImplementedError()

    def get_all(self) -> List[User]:
        raise NotImplementedError()


def add_tables(metadata: MetaData) -> None:
    Table(
        "users",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("email", String(length=256), nullable=False, unique=True),
    )


class DatabaseUserRepository(UserRepository):
    @inject.autoparams()
    def __init__(self, engine: Engine):
        self._engine = engine

    def add(self, *users: User) -> None:
        with self._engine.begin() as connection:
            for user in users:
                connection.execute(text("INSERT INTO users (email) VALUES (:email)"), {"email": user.email})

    def clear(self) -> None:
        with self._engine.begin() as connection:
            connection.execute(text("DELETE FROM users"))

    def get_by_email(self, email: str) -> User | None:
        with self._engine.connect() as connection:
            result = connection.execute(text("SELECT email FROM users WHERE email = :email"), {"email": email})
            row = result.one_or_none()
            return User(row.email) if row else None

    def get_all(self) -> List[User]:
        with self._engine.connect() as connection:
            result = connection.execute(text("SELECT email FROM users"))
            return [User(row.email) for row in result]


bp = Blueprint("users", __name__)


@bp.route("", methods=["POST"])
@api_key_auth
@inject.autoparams()
def add(users: UserRepository) -> Response:
    json = request.get_json()
    users.add(*[User(element["email"]) for element in json])
    return Response(status=201)


@bp.route("", methods=["DELETE"])
@api_key_auth
@inject.autoparams()
def clear(users: UserRepository) -> Response:
    users.clear()
    return Response(status=204)
