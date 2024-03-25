from typing import Generator

import pytest
from sqlalchemy import Engine, create_engine, event, text
from sqlalchemy.engine.interfaces import DBAPIConnection
from sqlalchemy.pool import ConnectionPoolEntry

from schemes.infrastructure.database import Base


@pytest.fixture(name="engine")
def engine_fixture() -> Generator[Engine, None, None]:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    event.listen(Engine, "connect", _enforce_sqlite_foreign_keys)
    _create_schemas(engine)
    Base.metadata.create_all(engine)
    yield engine
    event.remove(Engine, "connect", _enforce_sqlite_foreign_keys)


def _enforce_sqlite_foreign_keys(dbapi_connection: DBAPIConnection, _connection_record: ConnectionPoolEntry) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def _create_schemas(engine: Engine) -> None:
    with engine.connect() as connection:
        connection.execute(text("ATTACH DATABASE ':memory:' AS authority"))
        connection.commit()
