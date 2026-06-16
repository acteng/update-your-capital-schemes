from typing import Any, Generator, Mapping

import inject
import pytest
from _pytest.monkeypatch import MonkeyPatch
from sqlalchemy import Engine

from schemes.infrastructure.database import CapitalSchemeEntity


@pytest.mark.usefixtures("client")
class TestProdDatabase:
    @pytest.fixture(name="monkeypatch", scope="class")
    @classmethod
    def monkeypatch_fixture(cls) -> Generator[MonkeyPatch]:
        with pytest.MonkeyPatch.context() as monkeypatch:
            yield monkeypatch

    @pytest.fixture(name="env", scope="class", autouse=True)
    @classmethod
    def env_fixture(cls, monkeypatch: MonkeyPatch) -> None:
        monkeypatch.setenv("FLASK_ENV", "prod")

    @pytest.fixture(name="config", scope="class")
    @classmethod
    def config_fixture(cls, config: Mapping[str, Any]) -> Mapping[str, Any]:
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
