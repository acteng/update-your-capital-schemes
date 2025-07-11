import re
from datetime import datetime

import pytest

from schemes.domain.dates import DateRange
from schemes.domain.reporting_window import DefaultReportingWindowService, ReportingWindow


class TestReportingWindow:
    def test_cannot_create_without_to_date(self) -> None:
        window = DateRange(datetime(2020, 4, 1), None)

        with pytest.raises(ValueError, match=re.escape(f"Reporting window cannot be open-ended: {window}")):
            ReportingWindow(window)

    @pytest.mark.parametrize(
        "now, expected_days_left",
        [
            pytest.param(datetime(2020, 4, 24, 12), 7, id="days left"),
            pytest.param(datetime(2020, 5, 8, 12), 0, id="overdue"),
        ],
    )
    def test_days_left(self, now: datetime, expected_days_left: int) -> None:
        reporting_window = ReportingWindow(DateRange(datetime(2020, 4, 1), datetime(2020, 5, 1)))

        assert reporting_window.days_left(now) == expected_days_left


class TestDefaultReportingWindowService:
    @pytest.fixture(name="reporting_window_service")
    def reporting_window_service_fixture(self) -> DefaultReportingWindowService:
        return DefaultReportingWindowService()

    @pytest.mark.parametrize(
        "date, expected_window_start, expected_window_end",
        [
            pytest.param(datetime(2020, 1, 1), datetime(2020, 1, 1), datetime(2020, 2, 1), id="start of Q3"),
            pytest.param(datetime(2020, 1, 24), datetime(2020, 1, 1), datetime(2020, 2, 1), id="middle of Q3"),
            pytest.param(datetime(2020, 1, 31), datetime(2020, 1, 1), datetime(2020, 2, 1), id="end of Q3"),
            pytest.param(datetime(2020, 4, 24), datetime(2020, 4, 1), datetime(2020, 5, 1), id="middle of Q4"),
            pytest.param(datetime(2020, 7, 24), datetime(2020, 7, 1), datetime(2020, 8, 1), id="middle of Q1"),
            pytest.param(datetime(2020, 10, 24), datetime(2020, 10, 1), datetime(2020, 11, 1), id="middle of Q2"),
            pytest.param(datetime(2021, 1, 24), datetime(2021, 1, 1), datetime(2021, 2, 1), id="different year"),
            pytest.param(datetime(2020, 5, 24), datetime(2020, 4, 1), datetime(2020, 5, 1), id="last reporting window"),
        ],
    )
    def test_get_by_date(
        self,
        reporting_window_service: DefaultReportingWindowService,
        date: datetime,
        expected_window_start: datetime,
        expected_window_end: datetime,
    ) -> None:
        reporting_window = reporting_window_service.get_by_date(date)

        assert reporting_window == ReportingWindow(DateRange(expected_window_start, expected_window_end))
