import inject
from sqlalchemy import Engine, delete, select
from sqlalchemy.orm import Session

from schemes.domain.authorities import Authority, AuthorityRepository
from schemes.infrastructure.database import AuthorityEntity


class DatabaseAuthorityRepository(AuthorityRepository):
    @inject.autoparams()
    def __init__(self, engine: Engine):
        self._engine = engine

    def add(self, *authorities: Authority) -> None:
        with Session(self._engine) as session:
            session.add_all(
                AuthorityEntity(authority_full_name=authority.name, authority_abbreviation=authority.id)
                for authority in authorities
            )
            session.commit()

    def clear(self) -> None:
        with Session(self._engine) as session:
            session.execute(delete(AuthorityEntity))
            session.commit()

    def get(self, id_: str) -> Authority | None:
        with Session(self._engine) as session:
            result = session.scalars(select(AuthorityEntity).where(AuthorityEntity.authority_abbreviation == id_))
            row = result.one_or_none()
            return Authority(id_=row.authority_abbreviation, name=row.authority_full_name) if row else None
