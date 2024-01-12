import inject
from sqlalchemy import Engine, delete, insert, select

from schemes.domain.users import User, UserRepository
from schemes.infrastructure import user_table


class DatabaseUserRepository(UserRepository):
    @inject.autoparams()
    def __init__(self, engine: Engine):
        self._engine = engine

    def add(self, *users: User) -> None:
        with self._engine.begin() as connection:
            for user in users:
                connection.execute(insert(user_table).values(email=user.email, authority_id=user.authority_id))

    def clear(self) -> None:
        with self._engine.begin() as connection:
            connection.execute(delete(user_table))

    def get_by_email(self, email: str) -> User | None:
        with self._engine.connect() as connection:
            result = connection.execute(select(user_table).where(user_table.c.email == email))
            row = result.one_or_none()
            return User(email=row.email, authority_id=row.authority_id) if row else None
