from datetime import datetime

import pytest

from schemes.domain.dates import DateRange


class TestDateRange:
    def test_create(self) -> None:
        date_range = DateRange(datetime(2020, 1, 1), datetime(2020, 1, 31))

        assert date_range.date_from == datetime(2020, 1, 1) and date_range.date_to == datetime(2020, 1, 31)

    @pytest.mark.parametrize(
        "date_from, date_to",
        [
            (datetime(2020, 1, 1), datetime(2020, 1, 31)),
            (datetime(2020, 1, 31), datetime(2020, 1, 31)),
            (datetime(2020, 1, 1), None),
        ],
    )
    def test_date_from_before_or_equal_to_date_to(self, date_from: datetime, date_to: datetime | None) -> None:
        DateRange(date_from, date_to)

    def test_date_from_after_date_to_errors(self) -> None:
        with pytest.raises(
            ValueError, match="From date '2020-01-01 12:00:00' must not be after to date '2019-12-31 13:00:00'"
        ):
            DateRange(datetime(2020, 1, 1, 12), datetime(2019, 12, 31, 13))
