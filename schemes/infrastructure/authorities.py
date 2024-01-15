import inject
from sqlalchemy import Engine, delete
from sqlalchemy.orm import Session

from schemes.domain.authorities import Authority, AuthorityRepository
from schemes.infrastructure import AuthorityEntity


class DatabaseAuthorityRepository(AuthorityRepository):
    @inject.autoparams()
    def __init__(self, engine: Engine):
        self._engine = engine

    def add(self, *authorities: Authority) -> None:
        with Session(self._engine) as session:
            session.add_all(
                AuthorityEntity(authority_id=authority.id, authority_name=authority.name) for authority in authorities
            )
            session.commit()

    def clear(self) -> None:
        with Session(self._engine) as session:
            session.execute(delete(AuthorityEntity))
            session.commit()

    def get(self, id_: int) -> Authority | None:
        with Session(self._engine) as session:
            row = session.get(AuthorityEntity, id_)
            return Authority(id_=row.authority_id, name=row.authority_name) if row else None
