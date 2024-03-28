from typing import Generator

import pytest
from sqlalchemy import Engine, create_engine, text
from testcontainers.postgres import PostgresContainer

from schemes.infrastructure.database import Base


@pytest.fixture(name="engine")
def engine_fixture() -> Generator[Engine, None, None]:
    with PostgresContainer("postgres:15") as postgres:
        connection_url = postgres.get_connection_url(driver="pg8000")
        engine = create_engine(connection_url)
        _create_schemas(engine)
        Base.metadata.create_all(engine)
        yield engine


def _create_schemas(engine: Engine) -> None:
    with engine.connect() as connection:
        connection.execute(text("CREATE SCHEMA authority"))
        connection.execute(text("CREATE SCHEMA capital_scheme"))
        connection.commit()
