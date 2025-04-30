import inject
from sqlalchemy import delete, select
from sqlalchemy.orm import Session, sessionmaker

from schemes.domain.users import User, UserRepository
from schemes.infrastructure.database import UserEntity


class DatabaseUserRepository(UserRepository):
    @inject.autoparams()
    def __init__(self, session_maker: sessionmaker[Session]):
        self._session_maker = session_maker

    def add(self, *users: User) -> None:
        with self._session_maker() as session:
            session.add_all(
                UserEntity(email=user.email, authority_abbreviation=user.authority_abbreviation) for user in users
            )
            session.commit()

    def clear(self) -> None:
        with self._session_maker() as session:
            session.execute(delete(UserEntity))
            session.commit()

    def get(self, email: str) -> User | None:
        with self._session_maker() as session:
            result = session.scalars(select(UserEntity).where(UserEntity.email == email))
            row = result.one_or_none()
            return User(email=row.email, authority_abbreviation=row.authority_abbreviation) if row else None
