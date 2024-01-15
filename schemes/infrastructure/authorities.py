import inject
from sqlalchemy import Engine, delete, select
from sqlalchemy.orm import Session, raiseload

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
            result = session.scalars(
                select(AuthorityEntity).options(raiseload("*")).where(AuthorityEntity.authority_id == id_)
            )
            row = result.one_or_none()
            return Authority(id_=row.authority_id, name=row.authority_name) if row else None
