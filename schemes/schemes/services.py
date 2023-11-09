from typing import Any

import inject
from sqlalchemy import (
    Column,
    Engine,
    ForeignKey,
    Integer,
    MetaData,
    Row,
    Table,
    Text,
    text,
)

from schemes.schemes.domain import Scheme, SchemeType


class SchemeRepository:  # pylint:disable=duplicate-code
    def add(self, *schemes: Scheme) -> None:
        raise NotImplementedError()

    def clear(self) -> None:
        raise NotImplementedError()

    def get(self, id_: int) -> Scheme | None:
        raise NotImplementedError()

    def get_by_authority(self, authority_id: int) -> list[Scheme]:
        raise NotImplementedError()

    def get_all(self) -> list[Scheme]:
        raise NotImplementedError()


def add_tables(metadata: MetaData) -> None:
    Table(
        "capital_scheme",
        metadata,
        Column("capital_scheme_id", Integer, primary_key=True),
        Column("scheme_name", Text, nullable=False),
        Column(
            "bid_submitting_authority_id",
            Integer,
            ForeignKey("authority.authority_id", name="capital_scheme_bid_submitting_authority_id_fkey"),
        ),
        Column("scheme_type_id", Integer),
    )


class DatabaseSchemeRepository(SchemeRepository):
    _TYPE_IDS = {
        SchemeType.DEVELOPMENT: 1,
        SchemeType.CONSTRUCTION: 2,
    }

    @inject.autoparams()
    def __init__(self, engine: Engine):
        self._engine = engine

    def add(self, *schemes: Scheme) -> None:
        sql = """
            INSERT INTO capital_scheme (capital_scheme_id, scheme_name, bid_submitting_authority_id, scheme_type_id)
            VALUES (:capital_scheme_id, :scheme_name, :bid_submitting_authority_id, :scheme_type_id)
        """
        with self._engine.begin() as connection:
            for scheme in schemes:
                connection.execute(
                    text(sql),
                    {
                        "capital_scheme_id": scheme.id,
                        "scheme_name": scheme.name,
                        "bid_submitting_authority_id": scheme.authority_id,
                        "scheme_type_id": self._type_to_id(scheme.type) if scheme.type else None,
                    },
                )

    def clear(self) -> None:
        with self._engine.begin() as connection:
            connection.execute(text("DELETE FROM capital_scheme"))

    def get(self, id_: int) -> Scheme | None:
        sql = """
            SELECT capital_scheme_id, scheme_name, bid_submitting_authority_id, scheme_type_id FROM capital_scheme
            WHERE capital_scheme_id=:capital_scheme_id
        """
        with self._engine.connect() as connection:
            result = connection.execute(text(sql), {"capital_scheme_id": id_})
            row = result.one_or_none()
            return self._to_domain(row) if row else None

    def get_by_authority(self, authority_id: int) -> list[Scheme]:
        sql = """
            SELECT capital_scheme_id, scheme_name, bid_submitting_authority_id, scheme_type_id FROM capital_scheme
            WHERE bid_submitting_authority_id=:bid_submitting_authority_id
            ORDER BY capital_scheme_id
        """
        with self._engine.connect() as connection:
            result = connection.execute(text(sql), {"bid_submitting_authority_id": authority_id})
            return [self._to_domain(row) for row in result]

    def get_all(self) -> list[Scheme]:
        sql = """
            SELECT capital_scheme_id, scheme_name, bid_submitting_authority_id, scheme_type_id FROM capital_scheme
            ORDER BY capital_scheme_id
        """
        with self._engine.connect() as connection:
            result = connection.execute(text(sql))
            return [self._to_domain(row) for row in result]

    def _type_to_id(self, type_: SchemeType) -> int:
        return self._TYPE_IDS[type_]

    def _id_to_type(self, id_: int) -> SchemeType:
        return next(key for key, value in self._TYPE_IDS.items() if value == id_)

    def _to_domain(self, row: Row[Any]) -> Scheme:
        return Scheme(
            id_=row.capital_scheme_id,
            name=row.scheme_name,
            authority_id=row.bid_submitting_authority_id,
            type_=self._id_to_type(row.scheme_type_id) if row.scheme_type_id else None,
        )
