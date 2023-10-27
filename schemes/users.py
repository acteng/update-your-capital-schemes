from dataclasses import dataclass
from typing import List

import inject
from flask import Blueprint, Response, request
from sqlalchemy import Column, Engine, Integer, MetaData, String, Table, text

from schemes.auth.api_key import api_key_auth


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
        "user",
        metadata,
        Column("user_id", Integer, primary_key=True),
        Column("email", String(length=256), nullable=False, unique=True),
    )


class DatabaseUserRepository(UserRepository):
    @inject.autoparams()
    def __init__(self, engine: Engine):
        self._engine = engine

    def add(self, *users: User) -> None:
        with self._engine.begin() as connection:
            for user in users:
                connection.execute(text("INSERT INTO user (email) VALUES (:email)"), {"email": user.email})

    def clear(self) -> None:
        with self._engine.begin() as connection:
            connection.execute(text("DELETE FROM user"))

    def get_by_email(self, email: str) -> User | None:
        with self._engine.connect() as connection:
            result = connection.execute(text("SELECT email FROM user WHERE email = :email"), {"email": email})
            row = result.one_or_none()
            return User(row.email) if row else None

    def get_all(self) -> List[User]:
        with self._engine.connect() as connection:
            result = connection.execute(text("SELECT email FROM user"))
            return [User(row.email) for row in result]


bp = Blueprint("users", __name__)


@bp.post("")
@api_key_auth
@inject.autoparams()
def add(users: UserRepository) -> Response:
    users_repr = [UserRepr(**element) for element in request.get_json()]
    users.add(*[user_repr.to_domain() for user_repr in users_repr])
    return Response(status=201)


@bp.delete("")
@api_key_auth
@inject.autoparams()
def clear(users: UserRepository) -> Response:
    users.clear()
    return Response(status=204)


@dataclass
class UserRepr:
    email: str

    def to_domain(self) -> User:
        return User(email=self.email)
