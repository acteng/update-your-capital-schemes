import re

import pytest

from schemes.domain.schemes.data_sources import DataSource
from schemes.domain.schemes.financials import FinancialType, SchemeFinancial, SchemeFinancials


class TestSchemeFinancials:
    def test_create(self) -> None:
        financials = SchemeFinancials()

        assert financials.financials == []

    def test_get_financials_is_copy(self) -> None:
        financials = SchemeFinancials()
        financials.update_financial(
            SchemeFinancial(id_=1, type_=FinancialType.FUNDING_ALLOCATION, amount=100_000, source=DataSource.ATF4_BID)
        )

        financials.financials.clear()

        assert financials.financials

    def test_update_financial(self) -> None:
        financials = SchemeFinancials()
        financial = SchemeFinancial(
            id_=1, type_=FinancialType.FUNDING_ALLOCATION, amount=100_000, source=DataSource.ATF4_BID
        )

        financials.update_financial(financial)

        assert financials.financials == [financial]

    def test_cannot_update_financial_with_another_spend_to_date(self) -> None:
        financials = SchemeFinancials()
        financial = SchemeFinancial(
            id_=1, type_=FinancialType.SPEND_TO_DATE, amount=100_000, source=DataSource.ATF4_BID
        )
        financials.update_financial(financial)

        with pytest.raises(ValueError, match=re.escape(f"Spend to date already exists: {financial!r}")):
            financials.update_financial(
                SchemeFinancial(id_=2, type_=FinancialType.SPEND_TO_DATE, amount=200_000, source=DataSource.ATF4_BID)
            )

    def test_update_financials(self) -> None:
        financials = SchemeFinancials()
        financial1 = SchemeFinancial(
            id_=1, type_=FinancialType.FUNDING_ALLOCATION, amount=100_000, source=DataSource.ATF4_BID
        )
        financial2 = SchemeFinancial(
            id_=2, type_=FinancialType.EXPECTED_COST, amount=200_000, source=DataSource.ATF4_BID
        )

        financials.update_financials(financial1, financial2)

        assert financials.financials == [financial1, financial2]

    def test_update_spend_to_date_removes_current_financial(self) -> None:
        financials = SchemeFinancials()
        financials.update_financial(
            SchemeFinancial(id_=1, type_=FinancialType.SPEND_TO_DATE, amount=50_000, source=DataSource.ATF4_BID)
        )

        financials.update_spend_to_date(60_000)

        assert 1 not in (financial.id for financial in financials.financials)

    def test_update_spend_to_date_adds_new_financial(self) -> None:
        financials = SchemeFinancials()

        financials.update_spend_to_date(60_000)

        financial = financials.financials[0]
        assert (
            financial.id is None
            and financial.type == FinancialType.SPEND_TO_DATE
            and financial.amount == 60_000
            and financial.source == DataSource.AUTHORITY_UPDATE
        )

    def test_get_funding_allocation_sums_amounts(self) -> None:
        financials = SchemeFinancials()
        financials.update_financials(
            SchemeFinancial(id_=1, type_=FinancialType.FUNDING_ALLOCATION, amount=100_000, source=DataSource.ATF4_BID),
            SchemeFinancial(
                id_=2, type_=FinancialType.FUNDING_ALLOCATION, amount=20_000, source=DataSource.CHANGE_CONTROL
            ),
        )

        assert financials.funding_allocation == 120_000

    def test_get_funding_allocation_selects_financial_type(self) -> None:
        financials = SchemeFinancials()
        financials.update_financials(
            SchemeFinancial(id_=1, type_=FinancialType.FUNDING_ALLOCATION, amount=100_000, source=DataSource.ATF4_BID),
            SchemeFinancial(id_=2, type_=FinancialType.EXPECTED_COST, amount=200_000, source=DataSource.ATF4_BID),
        )

        assert financials.funding_allocation == 100_000

    def test_get_funding_allocation_when_no_matching_financials(self) -> None:
        financials = SchemeFinancials()
        financials.update_financial(
            SchemeFinancial(id_=1, type_=FinancialType.EXPECTED_COST, amount=100_000, source=DataSource.ATF4_BID)
        )

        assert financials.funding_allocation is None

    def test_get_funding_allocation_when_no_financials(self) -> None:
        financials = SchemeFinancials()

        assert financials.funding_allocation is None

    def test_get_spend_to_date(self) -> None:
        financials = SchemeFinancials()
        financials.update_financial(
            SchemeFinancial(id_=1, type_=FinancialType.SPEND_TO_DATE, amount=100_000, source=DataSource.ATF4_BID)
        )

        assert financials.spend_to_date == 100_000

    def test_get_spend_to_date_selects_financial_type(self) -> None:
        financials = SchemeFinancials()
        financials.update_financials(
            SchemeFinancial(id_=1, type_=FinancialType.SPEND_TO_DATE, amount=100_000, source=DataSource.ATF4_BID),
            SchemeFinancial(id_=2, type_=FinancialType.EXPECTED_COST, amount=200_000, source=DataSource.ATF4_BID),
        )

        assert financials.spend_to_date == 100_000

    def test_get_spend_to_date_when_no_matching_financials(self) -> None:
        financials = SchemeFinancials()
        financials.update_financial(
            SchemeFinancial(id_=1, type_=FinancialType.EXPECTED_COST, amount=100_000, source=DataSource.ATF4_BID)
        )

        assert financials.spend_to_date is None

    def test_get_spend_to_date_when_no_financials(self) -> None:
        financials = SchemeFinancials()

        assert financials.spend_to_date is None

    def test_get_allocation_still_to_spend(self) -> None:
        financials = SchemeFinancials()
        financials.update_financials(
            SchemeFinancial(id_=1, type_=FinancialType.FUNDING_ALLOCATION, amount=100_000, source=DataSource.ATF4_BID),
            SchemeFinancial(id_=2, type_=FinancialType.SPEND_TO_DATE, amount=50_000, source=DataSource.ATF4_BID),
        )

        assert financials.allocation_still_to_spend == 50_000

    def test_get_allocation_still_to_spend_when_no_funding_allocation(self) -> None:
        financials = SchemeFinancials()
        financials.update_financials(
            SchemeFinancial(id_=1, type_=FinancialType.SPEND_TO_DATE, amount=50_000, source=DataSource.ATF4_BID)
        )

        assert financials.allocation_still_to_spend == -50_000

    def test_get_allocation_still_to_spend_when_no_spend_to_date(self) -> None:
        financials = SchemeFinancials()
        financials.update_financials(
            SchemeFinancial(id_=1, type_=FinancialType.FUNDING_ALLOCATION, amount=100_000, source=DataSource.ATF4_BID)
        )

        assert financials.allocation_still_to_spend == 100_000

    def test_get_allocation_still_to_spend_when_no_financials(self) -> None:
        financials = SchemeFinancials()

        assert financials.allocation_still_to_spend == 0


class TestSchemeFinancial:
    def test_create(self) -> None:
        financial = SchemeFinancial(
            id_=1, type_=FinancialType.FUNDING_ALLOCATION, amount=100_000, source=DataSource.ATF4_BID
        )

        assert (
            financial.id == 1
            and financial.type == FinancialType.FUNDING_ALLOCATION
            and financial.amount == 100_000
            and financial.source == DataSource.ATF4_BID
        )

    @pytest.mark.parametrize(
        "type_, expected", [(FinancialType.FUNDING_ALLOCATION, True), (FinancialType.SPEND_TO_DATE, False)]
    )
    def test_is_funding_allocation(self, type_: FinancialType, expected: bool) -> None:
        financial = SchemeFinancial(id_=1, type_=type_, amount=0, source=DataSource.ATF4_BID)

        assert financial.is_funding_allocation == expected

    @pytest.mark.parametrize(
        "type_, expected", [(FinancialType.SPEND_TO_DATE, True), (FinancialType.FUNDING_ALLOCATION, False)]
    )
    def test_is_spend_to_date(self, type_: FinancialType, expected: bool) -> None:
        financial = SchemeFinancial(id_=1, type_=type_, amount=0, source=DataSource.ATF4_BID)

        assert financial.is_spend_to_date == expected
