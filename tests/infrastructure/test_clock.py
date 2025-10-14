from datetime import datetime
from typing import Any
from unittest.mock import patch

import pytest

from schemes.infrastructure.clock import FakeClock, SystemClock


class TestSystemClock:
    @pytest.fixture(name="clock")
    def clock_fixture(self) -> SystemClock:
        return SystemClock()

    @patch("schemes.infrastructure.clock.datetime")
    def test_get_now(self, mock_datetime: Any, clock: SystemClock) -> None:
        mock_datetime.now.return_value = datetime(2020, 1, 2, 12)

        assert clock.now == datetime(2020, 1, 2, 12)

    def test_cannot_set_now(self, clock: SystemClock) -> None:
        with pytest.raises(NotImplementedError):
            clock.now = datetime(2020, 1, 2)


class TestFakeClock:
    @pytest.fixture(name="clock")
    def clock_fixture(self) -> FakeClock:
        return FakeClock()

    def test_get_now_initially_returns_epoch(self, clock: FakeClock) -> None:
        assert clock.now == datetime(1970, 1, 1)

    def test_set_now(self, clock: FakeClock) -> None:
        clock.now = datetime(2020, 1, 2, 12)

        assert clock.now == datetime(2020, 1, 2, 12)
