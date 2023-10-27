from dataclasses import dataclass
from typing import List

import inject
from flask import Blueprint, Response, request
from sqlalchemy import Column, Engine, Integer, MetaData, Table, Text, text

from schemes.auth.api_key import api_key_auth
from schemes.users import UserRepository, UserRepr


@dataclass
class Authority:
    id: int
    name: str


class AuthorityRepository:  # pylint:disable=duplicate-code
    def add(self, *authorities: Authority) -> None:
        raise NotImplementedError()

    def clear(self) -> None:
        raise NotImplementedError()

    def get(self, id_: int) -> Authority | None:
        raise NotImplementedError()

    def get_all(self) -> List[Authority]:
        raise NotImplementedError()


def add_tables(metadata: MetaData) -> None:
    Table(
        "authority",
        metadata,
        Column("authority_id", Integer, primary_key=True),
        Column("authority_name", Text, nullable=False, unique=True),
    )


class DatabaseAuthorityRepository(AuthorityRepository):
    @inject.autoparams()
    def __init__(self, engine: Engine):
        self._engine = engine

    def add(self, *authorities: Authority) -> None:
        with self._engine.begin() as connection:
            for authority in authorities:
                connection.execute(
                    text(
                        "INSERT INTO authority (authority_id, authority_name) VALUES (:authority_id, :authority_name)"
                    ),
                    {"authority_id": authority.id, "authority_name": authority.name},
                )

    def clear(self) -> None:
        with self._engine.begin() as connection:
            connection.execute(text("DELETE FROM authority"))

    def get(self, id_: int) -> Authority | None:
        with self._engine.connect() as connection:
            result = connection.execute(
                text("SELECT authority_id, authority_name FROM authority WHERE authority_id = :authority_id"),
                {"authority_id": id_},
            )
            row = result.one_or_none()
            return Authority(id=row.authority_id, name=row.authority_name) if row else None

    def get_all(self) -> List[Authority]:
        with self._engine.connect() as connection:
            result = connection.execute(text("SELECT authority_id, authority_name FROM authority"))
            return [Authority(id=row.authority_id, name=row.authority_name) for row in result]


bp = Blueprint("authorities", __name__)


@bp.post("")
@api_key_auth
@inject.autoparams()
def add(authorities: AuthorityRepository) -> Response:
    authorities_repr = [AuthorityRepr(**element) for element in request.get_json()]
    authorities.add(*[authority_repr.to_domain() for authority_repr in authorities_repr])
    return Response(status=201)


@bp.post("<int:authority_id>/users")
@api_key_auth
@inject.autoparams("users")
def add_users(users: UserRepository, authority_id: int) -> Response:
    users_repr = [UserRepr(**element) for element in request.get_json()]
    users.add(*[user_repr.to_domain(authority_id) for user_repr in users_repr])
    return Response(status=201)


@bp.delete("")
@api_key_auth
@inject.autoparams()
def clear(authorities: AuthorityRepository) -> Response:
    authorities.clear()
    return Response(status=204)


@dataclass
class AuthorityRepr:
    id: int
    name: str

    def to_domain(self) -> Authority:
        return Authority(id=self.id, name=self.name)
