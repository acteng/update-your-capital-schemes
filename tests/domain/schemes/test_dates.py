from datetime import date

import pytest

from schemes.domain.schemes import DateRange


class TestDateRange:
    @pytest.mark.parametrize(
        "date_from, date_to",
        [(date(2020, 1, 1), date(2020, 1, 31)), (date(2020, 1, 31), date(2020, 1, 31)), (date(2020, 1, 1), None)],
    )
    def test_date_from_before_or_equal_to_date_to(self, date_from: date, date_to: date | None) -> None:
        DateRange(date_from, date_to)

    def test_date_from_after_date_to_errors(self) -> None:
        with pytest.raises(ValueError, match="From date '2020-01-01' must not be after to date '2019-12-31'"):
            DateRange(date(2020, 1, 1), date(2019, 12, 31))
