from datetime import datetime
from typing import Any, Mapping

import pytest
from flask.testing import FlaskClient

from schemes.infrastructure.clock import Clock


class TestClockApi:
    @pytest.fixture(name="config")
    def config_fixture(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        return dict(config) | {"API_KEY": "boardman"}

    def test_set_clock(self, clock: Clock, client: FlaskClient) -> None:
        clock.now = datetime(2020, 1, 1, 12)

        response = client.put(
            "/clock", headers={"Authorization": "API-Key boardman"}, data={"now": "2020-01-02T13:00:00"}
        )

        assert response.status_code == 204
        assert clock.now == datetime(2020, 1, 2, 13)

    def test_cannot_set_clock_when_no_credentials(self, clock: Clock, client: FlaskClient) -> None:
        clock.now = datetime(2020, 1, 1, 12)

        response = client.put("/clock", data={"now": "2020-01-02T13:00:00"})

        assert response.status_code == 401
        assert clock.now == datetime(2020, 1, 1, 12)

    def test_cannot_clear_users_when_incorrect_credentials(self, clock: Clock, client: FlaskClient) -> None:
        clock.now = datetime(2020, 1, 1, 12)

        response = client.put("/clock", headers={"Authorization": "API-Key obree"}, data={"now": "2020-01-02T13:00:00"})

        assert response.status_code == 401
        assert clock.now == datetime(2020, 1, 1, 12)


class TestClockApiWhenDisabled:
    def test_cannot_set_clock(self, clock: Clock, client: FlaskClient) -> None:
        clock.now = datetime(2020, 1, 1, 12)

        response = client.put(
            "/clock", headers={"Authorization": "API-Key boardman"}, data={"now": "2020-01-02T13:00:00"}
        )

        assert response.status_code == 401
        assert clock.now == datetime(2020, 1, 1, 12)
