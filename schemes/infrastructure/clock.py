from datetime import datetime, timedelta


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
        # TODO: remove once showcased
        # return datetime.now()
        return datetime.now() + timedelta(weeks=4)

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
