import inject
from sqlalchemy import delete
from sqlalchemy.orm import Session, sessionmaker

from schemes.domain.authorities import Authority, AuthorityRepository
from schemes.infrastructure.database import AuthorityEntity


class DatabaseAuthorityRepository(AuthorityRepository):
    @inject.autoparams()
    def __init__(self, session_maker: sessionmaker[Session]):
        self._session_maker = session_maker

    def add(self, *authorities: Authority) -> None:
        with self._session_maker() as session:
            session.add_all(
                AuthorityEntity(authority_id=authority.id, authority_full_name=authority.name)
                for authority in authorities
            )
            session.commit()

    def clear(self) -> None:
        with self._session_maker() as session:
            session.execute(delete(AuthorityEntity))
            session.commit()

    def get(self, id_: int) -> Authority | None:
        with self._session_maker() as session:
            row = session.get(AuthorityEntity, id_)
            return Authority(id_=row.authority_id, name=row.authority_full_name) if row else None
