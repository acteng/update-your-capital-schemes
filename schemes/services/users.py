import inject
from sqlalchemy import (
    Column,
    Engine,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    delete,
    insert,
    select,
)

from schemes.domain.users import User


class UserRepository:
    def add(self, *users: User) -> None:
        raise NotImplementedError()

    def clear(self) -> None:
        raise NotImplementedError()

    def get_by_email(self, email: str) -> User | None:
        raise NotImplementedError()

    def get_all(self) -> list[User]:
        raise NotImplementedError()


def add_tables(metadata: MetaData) -> None:
    Table(
        "user",
        metadata,
        Column("user_id", Integer, primary_key=True),
        Column("email", String(length=256), nullable=False, unique=True),
        Column(
            "authority_id", Integer, ForeignKey("authority.authority_id", name="user_authority_id_fkey"), nullable=False
        ),
    )


class DatabaseUserRepository(UserRepository):
    @inject.autoparams()
    def __init__(self, engine: Engine):
        self._engine = engine
        metadata = MetaData()
        add_tables(metadata)
        self._user_table = metadata.tables["user"]

    def add(self, *users: User) -> None:
        with self._engine.begin() as connection:
            for user in users:
                connection.execute(insert(self._user_table).values(email=user.email, authority_id=user.authority_id))

    def clear(self) -> None:
        with self._engine.begin() as connection:
            connection.execute(delete(self._user_table))

    def get_by_email(self, email: str) -> User | None:
        with self._engine.connect() as connection:
            result = connection.execute(select(self._user_table).where(self._user_table.c.email == email))
            row = result.one_or_none()
            return User(email=row.email, authority_id=row.authority_id) if row else None

    def get_all(self) -> list[User]:
        with self._engine.connect() as connection:
            result = connection.execute(select(self._user_table))
            return [User(email=row.email, authority_id=row.authority_id) for row in result]
