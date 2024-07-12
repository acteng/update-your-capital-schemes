from typing import Any, Mapping

import inject
import pytest
from sqlalchemy import Engine

from schemes.infrastructure.database import CapitalSchemeEntity


@pytest.mark.usefixtures("client")
class TestDatabase:
    @pytest.fixture(name="config", scope="class")
    def config_fixture(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        return dict(config) | {"CAPITAL_SCHEMES_DATABASE_URI": "sqlite+pysqlite:///:memory:"}

    def test_pool_pings_connections(self) -> None:
        engine = inject.instance(Engine)

        assert engine.pool._pre_ping is True

    def test_pool_recycles_connections(self) -> None:
        engine = inject.instance(Engine)

        assert engine.pool._recycle == 1800

    def test_capital_schemes_pool_pings_connections(self) -> None:
        engine = inject.instance((Engine, CapitalSchemeEntity))

        assert isinstance(engine, Engine) and engine.pool._pre_ping is True

    def test_capital_schemes_pool_recycles_connections(self) -> None:
        engine = inject.instance((Engine, CapitalSchemeEntity))

        assert isinstance(engine, Engine) and engine.pool._recycle == 1800
