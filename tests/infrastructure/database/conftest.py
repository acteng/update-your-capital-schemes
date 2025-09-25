from typing import Generator

import pytest
from sqlalchemy import Engine, create_engine, event, text
from sqlalchemy.engine.interfaces import DBAPIConnection
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import ConnectionPoolEntry

from schemes.infrastructure.database import Base


@pytest.fixture(name="engine")
def engine_fixture() -> Generator[Engine]:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    event.listen(Engine, "connect", _enforce_sqlite_foreign_keys)
    _create_schemas(engine)
    Base.metadata.create_all(engine)
    yield engine
    event.remove(Engine, "connect", _enforce_sqlite_foreign_keys)


@pytest.fixture(name="session_maker")
def session_maker_fixture(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(engine)


def _enforce_sqlite_foreign_keys(dbapi_connection: DBAPIConnection, _connection_record: ConnectionPoolEntry) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def _create_schemas(engine: Engine) -> None:
    with engine.connect() as connection:
        connection.execute(text("ATTACH DATABASE ':memory:' AS authority"))
        connection.execute(text("ATTACH DATABASE ':memory:' AS capital_scheme"))
        connection.commit()
