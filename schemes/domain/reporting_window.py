from dataclasses import dataclass
from datetime import datetime

from schemes.domain.dates import DateRange


@dataclass(frozen=True)
class ReportingWindow:
    window: DateRange

    def __post_init__(self) -> None:
        if self.window.date_to is None:
            raise ValueError(f"Reporting window cannot be open-ended: {self.window}")

    def days_left(self, now: datetime) -> int:
        assert self.window.date_to
        time_left = self.window.date_to - now
        return max(time_left.days + 1, 0)


class ReportingWindowService:
    def get_by_date(self, date: datetime) -> ReportingWindow:
        raise NotImplementedError()


class DefaultReportingWindowService(ReportingWindowService):
    def get_by_date(self, date: datetime) -> ReportingWindow:
        reporting_month = date.month - (date.month - 1) % 3
        start_date = datetime(date.year, reporting_month, 1)
        end_date = datetime(date.year, reporting_month + 1, 1)
        return ReportingWindow(DateRange(start_date, end_date))
