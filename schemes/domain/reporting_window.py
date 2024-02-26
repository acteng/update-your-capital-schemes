from dataclasses import dataclass
from datetime import datetime
from typing import Generator

from schemes.domain.dates import DateRange


@dataclass(frozen=True)
class ReportingWindow:
    window: DateRange

    def __post_init__(self) -> None:
        if self.window.date_to is None:
            raise ValueError(f"Reporting window cannot be open-ended: {self.window}")

    def days_left(self, now: datetime) -> int:
        assert self.window.date_to
        return (self.window.date_to - now).days + 1


class ReportingWindowService:
    def get_by_date(self, date: datetime) -> ReportingWindow | None:
        raise NotImplementedError()


class DefaultReportingWindowService(ReportingWindowService):
    def get_by_date(self, date: datetime) -> ReportingWindow | None:
        for reporting_window in self._reporting_windows(date.year):
            assert reporting_window.window.date_to
            if reporting_window.window.date_from <= date < reporting_window.window.date_to:
                return reporting_window
        return None

    @staticmethod
    def _reporting_windows(year: int) -> Generator[ReportingWindow, None, None]:
        for month in range(1, 12, 3):
            yield ReportingWindow(DateRange(datetime(year, month, 1), datetime(year, month + 1, 1)))
        # TODO: remove once showcased
        yield ReportingWindow(DateRange(datetime(2024, 2, 1), datetime(2024, 3, 1)))
