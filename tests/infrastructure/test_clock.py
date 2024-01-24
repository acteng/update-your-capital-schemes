from datetime import datetime
from unittest.mock import patch

import pytest

from schemes.infrastructure.clock import FakeClock, SystemClock


class TestSystemClock:
    @pytest.fixture(name="clock")
    def clock_fixture(self) -> SystemClock:
        return SystemClock()

    def test_get_now(self, clock: SystemClock) -> None:
        with patch("schemes.infrastructure.clock.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2020, 1, 2, 12)
            
            assert clock.now == datetime(2020, 1, 2, 12)

    def test_set_now(self, clock: SystemClock) -> None:
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
