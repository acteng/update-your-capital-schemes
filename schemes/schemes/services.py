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
    delete,
    insert,
    select,
)

from schemes.schemes.domain import FundingProgramme, Scheme, SchemeType


class SchemeRepository:
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
        Column("funding_programme_id", Integer),
    )


class DatabaseSchemeRepository(SchemeRepository):
    @inject.autoparams()
    def __init__(self, engine: Engine):
        self._engine = engine
        metadata = MetaData()
        add_tables(metadata)
        self._capital_scheme_table = metadata.tables["capital_scheme"]
        self._type_mapper = SchemeTypeMapper()
        self._funding_programme_mapper = FundingProgrammeMapper()

    def add(self, *schemes: Scheme) -> None:
        with self._engine.begin() as connection:
            for scheme in schemes:
                connection.execute(
                    insert(self._capital_scheme_table).values(
                        capital_scheme_id=scheme.id,
                        scheme_name=scheme.name,
                        bid_submitting_authority_id=scheme.authority_id,
                        scheme_type_id=self._type_mapper.to_id(scheme.type) if scheme.type else None,
                        funding_programme_id=self._funding_programme_mapper.to_id(scheme.funding_programme)
                        if scheme.funding_programme
                        else None,
                    )
                )

    def clear(self) -> None:
        with self._engine.begin() as connection:
            connection.execute(delete(self._capital_scheme_table))

    def get(self, id_: int) -> Scheme | None:
        with self._engine.connect() as connection:
            result = connection.execute(
                select(self._capital_scheme_table).where(self._capital_scheme_table.c.capital_scheme_id == id_)
            )
            row = result.one_or_none()
            return self._to_domain(row) if row else None

    def get_by_authority(self, authority_id: int) -> list[Scheme]:
        with self._engine.connect() as connection:
            result = connection.execute(
                select(self._capital_scheme_table)
                .where(self._capital_scheme_table.c.bid_submitting_authority_id == authority_id)
                .order_by(self._capital_scheme_table.c.capital_scheme_id)
            )
            return [self._to_domain(row) for row in result]

    def get_all(self) -> list[Scheme]:
        with self._engine.connect() as connection:
            result = connection.execute(
                select(self._capital_scheme_table).order_by(self._capital_scheme_table.c.capital_scheme_id)
            )
            return [self._to_domain(row) for row in result]

    def _to_domain(self, row: Row[Any]) -> Scheme:
        scheme = Scheme(id_=row.capital_scheme_id, name=row.scheme_name, authority_id=row.bid_submitting_authority_id)
        scheme.type = self._type_mapper.to_domain(row.scheme_type_id)
        scheme.funding_programme = self._funding_programme_mapper.to_domain(row.funding_programme_id)
        return scheme


class SchemeTypeMapper:
    _TYPE_IDS = {
        SchemeType.DEVELOPMENT: 1,
        SchemeType.CONSTRUCTION: 2,
    }

    def to_id(self, type_: SchemeType | None) -> int | None:
        return self._TYPE_IDS[type_] if type_ else None

    def to_domain(self, id_: int | None) -> SchemeType | None:
        return next(key for key, value in self._TYPE_IDS.items() if value == id_) if id_ else None


class FundingProgrammeMapper:
    _FUNDING_PROGRAMME_IDS = {
        FundingProgramme.ATF2: 1,
        FundingProgramme.ATF3: 2,
        FundingProgramme.ATF4: 3,
        FundingProgramme.ATF4E: 4,
        FundingProgramme.ATF5: 5,
        FundingProgramme.MRN: 6,
        FundingProgramme.LUF: 7,
        FundingProgramme.CRSTS: 8,
    }

    def to_id(self, funding_programme: FundingProgramme | None) -> int | None:
        return self._FUNDING_PROGRAMME_IDS[funding_programme] if funding_programme else None

    def to_domain(self, id_: int | None) -> FundingProgramme | None:
        return next(key for key, value in self._FUNDING_PROGRAMME_IDS.items() if value == id_) if id_ else None
