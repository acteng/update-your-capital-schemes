import inject
from sqlalchemy import Column, Engine, Integer, MetaData, Table, Text, text

from schemes.authorities.domain import Authority


class AuthorityRepository:
    def add(self, *authorities: Authority) -> None:
        raise NotImplementedError()

    def clear(self) -> None:
        raise NotImplementedError()

    def get(self, id_: int) -> Authority | None:
        raise NotImplementedError()

    def get_all(self) -> list[Authority]:
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
            return Authority(id_=row.authority_id, name=row.authority_name) if row else None

    def get_all(self) -> list[Authority]:
        with self._engine.connect() as connection:
            result = connection.execute(text("SELECT authority_id, authority_name FROM authority"))
            return [Authority(id_=row.authority_id, name=row.authority_name) for row in result]
