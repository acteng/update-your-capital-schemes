from datetime import date

import pytest
from _decimal import Decimal

from schemes.domain.schemes.dates import DateRange
from schemes.domain.schemes.funding import DataSource, FinancialRevision, FinancialType


class TestFinancialRevision:
    @pytest.mark.parametrize(
        "effective_date_to, type_, source, expected",
        [
            (None, FinancialType.FUNDING_ALLOCATION, DataSource.ATF4_BID, True),
            (date(2000, 1, 31), FinancialType.FUNDING_ALLOCATION, DataSource.ATF4_BID, False),
            (None, FinancialType.SPENT_TO_DATE, DataSource.ATF4_BID, False),
            (None, FinancialType.FUNDING_ALLOCATION, DataSource.CHANGE_CONTROL, False),
        ],
    )
    def test_is_current_funding_allocation(
        self, effective_date_to: date, type_: FinancialType, source: DataSource, expected: bool
    ) -> None:
        financial_revision = FinancialRevision(
            effective=DateRange(date(2000, 1, 1), effective_date_to), type=type_, amount=Decimal(0), source=source
        )

        assert financial_revision.is_current_funding_allocation == expected

    @pytest.mark.parametrize(
        "effective_date_to, type_, expected",
        [
            (None, FinancialType.SPENT_TO_DATE, True),
            (date(2000, 1, 31), FinancialType.SPENT_TO_DATE, False),
            (None, FinancialType.FUNDING_ALLOCATION, False),
        ],
    )
    def test_is_current_spent_to_date(self, effective_date_to: date, type_: FinancialType, expected: bool) -> None:
        financial_revision = FinancialRevision(
            effective=DateRange(date(2000, 1, 1), effective_date_to),
            type=type_,
            amount=Decimal(0),
            source=DataSource.ATF4_BID,
        )

        assert financial_revision.is_current_spent_to_date == expected
