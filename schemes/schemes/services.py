import inject
from sqlalchemy import Column, Engine, ForeignKey, Integer, MetaData, Table, Text, text

from schemes.schemes.domain import Scheme


class SchemeRepository:  # pylint:disable=duplicate-code
    def add(self, *schemes: Scheme) -> None:
        raise NotImplementedError()

    def clear(self) -> None:
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
    )


class DatabaseSchemeRepository(SchemeRepository):
    @inject.autoparams()
    def __init__(self, engine: Engine):
        self._engine = engine

    def add(self, *schemes: Scheme) -> None:
        with self._engine.begin() as connection:
            for scheme in schemes:
                connection.execute(
                    text(
                        "INSERT INTO capital_scheme (capital_scheme_id, scheme_name, bid_submitting_authority_id) "
                        "VALUES (:capital_scheme_id, :scheme_name, :bid_submitting_authority_id)"
                    ),
                    {
                        "capital_scheme_id": scheme.id,
                        "scheme_name": scheme.name,
                        "bid_submitting_authority_id": scheme.authority_id,
                    },
                )

    def clear(self) -> None:
        with self._engine.begin() as connection:
            connection.execute(text("DELETE FROM capital_scheme"))

    def get_by_authority(self, authority_id: int) -> list[Scheme]:
        with self._engine.connect() as connection:
            result = connection.execute(
                text(
                    "SELECT capital_scheme_id, scheme_name, bid_submitting_authority_id FROM capital_scheme "
                    "WHERE bid_submitting_authority_id=:bid_submitting_authority_id "
                    "ORDER BY capital_scheme_id"
                ),
                {"bid_submitting_authority_id": authority_id},
            )
            return [
                Scheme(id=row.capital_scheme_id, name=row.scheme_name, authority_id=row.bid_submitting_authority_id)
                for row in result
            ]

    def get_all(self) -> list[Scheme]:
        with self._engine.connect() as connection:
            result = connection.execute(
                text(
                    "SELECT capital_scheme_id, scheme_name, bid_submitting_authority_id FROM capital_scheme "
                    "ORDER BY capital_scheme_id"
                )
            )
            return [
                Scheme(id=row.capital_scheme_id, name=row.scheme_name, authority_id=row.bid_submitting_authority_id)
                for row in result
            ]
