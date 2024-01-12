import inject
from sqlalchemy import Engine, delete, insert, select

from schemes.domain.authorities import Authority, AuthorityRepository
from schemes.infrastructure import authority_table


class DatabaseAuthorityRepository(AuthorityRepository):
    @inject.autoparams()
    def __init__(self, engine: Engine):
        self._engine = engine

    def add(self, *authorities: Authority) -> None:
        with self._engine.begin() as connection:
            for authority in authorities:
                connection.execute(
                    insert(authority_table).values(authority_id=authority.id, authority_name=authority.name)
                )

    def clear(self) -> None:
        with self._engine.begin() as connection:
            connection.execute(delete(authority_table))

    def get(self, id_: int) -> Authority | None:
        with self._engine.connect() as connection:
            result = connection.execute(select(authority_table).where(authority_table.c.authority_id == id_))
            row = result.one_or_none()
            return Authority(id_=row.authority_id, name=row.authority_name) if row else None
