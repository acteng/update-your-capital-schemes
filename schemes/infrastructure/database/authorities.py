import inject
from sqlalchemy import delete, select
from sqlalchemy.orm import Session, sessionmaker

from schemes.domain.authorities import Authority, AuthorityRepository
from schemes.infrastructure.database import AuthorityEntity


class DatabaseAuthorityRepository(AuthorityRepository):
    @inject.autoparams()
    def __init__(self, session_maker: sessionmaker[Session]):
        self._session_maker = session_maker

    async def add(self, *authorities: Authority) -> None:
        with self._session_maker() as session:
            session.add_all(
                AuthorityEntity(authority_abbreviation=authority.abbreviation, authority_full_name=authority.name)
                for authority in authorities
            )
            session.commit()

    async def clear(self) -> None:
        with self._session_maker() as session:
            session.execute(delete(AuthorityEntity))
            session.commit()

    async def get(self, abbreviation: str) -> Authority | None:
        with self._session_maker() as session:
            result = session.scalars(
                select(AuthorityEntity).where(AuthorityEntity.authority_abbreviation == abbreviation)
            )
            row = result.one_or_none()
            return Authority(abbreviation=row.authority_abbreviation, name=row.authority_full_name) if row else None
