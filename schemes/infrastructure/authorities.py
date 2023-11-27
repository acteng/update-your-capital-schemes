import inject
from sqlalchemy import (
    Column,
    Engine,
    Integer,
    MetaData,
    Table,
    Text,
    delete,
    insert,
    select,
)

from schemes.domain.authorities import Authority, AuthorityRepository


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
        metadata = MetaData()
        add_tables(metadata)
        self._authority_table = metadata.tables["authority"]

    def add(self, *authorities: Authority) -> None:
        with self._engine.begin() as connection:
            for authority in authorities:
                connection.execute(
                    insert(self._authority_table).values(authority_id=authority.id, authority_name=authority.name)
                )

    def clear(self) -> None:
        with self._engine.begin() as connection:
            connection.execute(delete(self._authority_table))

    def get(self, id_: int) -> Authority | None:
        with self._engine.connect() as connection:
            result = connection.execute(
                select(self._authority_table).where(self._authority_table.c.authority_id == id_)
            )
            row = result.one_or_none()
            return Authority(id_=row.authority_id, name=row.authority_name) if row else None
