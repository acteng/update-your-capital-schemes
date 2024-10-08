from datetime import datetime


class Clock:
    @property
    def now(self) -> datetime:
        raise NotImplementedError()

    @now.setter
    def now(self, now: datetime) -> None:
        raise NotImplementedError()


class SystemClock(Clock):
    @property
    def now(self) -> datetime:
        return datetime.now()

    @now.setter
    def now(self, now: datetime) -> None:
        raise NotImplementedError()


class FakeClock(Clock):
    def __init__(self) -> None:
        self._now = datetime(1970, 1, 1)

    @property
    def now(self) -> datetime:
        return self._now

    @now.setter
    def now(self, now: datetime) -> None:
        self._now = now
