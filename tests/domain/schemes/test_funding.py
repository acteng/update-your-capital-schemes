import re
from datetime import datetime

import pytest

from schemes.domain.dates import DateRange
from schemes.domain.schemes import (
    BidStatus,
    BidStatusRevision,
    DataSource,
    FinancialRevision,
    FinancialType,
    SchemeFunding,
)


class TestSchemeFunding:
    def test_create(self) -> None:
        funding = SchemeFunding()

        assert funding.bid_status_revisions == [] and funding.financial_revisions == []

    def test_get_bid_status_revisions_is_copy(self) -> None:
        funding = SchemeFunding()
        funding.update_bid_status(
            BidStatusRevision(id_=1, effective=DateRange(datetime(2020, 1, 1), None), status=BidStatus.FUNDED)
        )

        funding.bid_status_revisions.clear()

        assert funding.bid_status_revisions

    def test_update_bid_status(self) -> None:
        funding = SchemeFunding()
        bid_status_revision = BidStatusRevision(
            id_=1, effective=DateRange(datetime(2020, 1, 1), None), status=BidStatus.FUNDED
        )

        funding.update_bid_status(bid_status_revision)

        assert funding.bid_status_revisions == [bid_status_revision]

    def test_cannot_update_bid_status_with_another_current_bid_status(self) -> None:
        funding = SchemeFunding()
        bid_status_revision = BidStatusRevision(
            id_=1, effective=DateRange(datetime(2020, 1, 1), None), status=BidStatus.SUBMITTED
        )
        funding.update_bid_status(bid_status_revision)

        with pytest.raises(
            ValueError, match=re.escape(f"Current bid status already exists: {repr(bid_status_revision)}")
        ):
            funding.update_bid_status(
                BidStatusRevision(id_=2, effective=DateRange(datetime(2020, 1, 1), None), status=BidStatus.FUNDED)
            )

    def test_update_bid_statuses(self) -> None:
        funding = SchemeFunding()
        bid_status_revision1 = BidStatusRevision(
            id_=1, effective=DateRange(datetime(2020, 1, 1), datetime(2020, 2, 1)), status=BidStatus.SUBMITTED
        )
        bid_status_revision2 = BidStatusRevision(
            id_=2, effective=DateRange(datetime(2020, 2, 1), None), status=BidStatus.FUNDED
        )

        funding.update_bid_statuses(bid_status_revision1, bid_status_revision2)

        assert funding.bid_status_revisions == [bid_status_revision1, bid_status_revision2]

    def test_get_bid_status(self) -> None:
        funding = SchemeFunding()
        funding.update_bid_status(
            BidStatusRevision(
                id_=1, effective=DateRange(datetime(2020, 1, 1), datetime(2020, 2, 1)), status=BidStatus.SUBMITTED
            )
        )
        funding.update_bid_status(
            BidStatusRevision(id_=2, effective=DateRange(datetime(2020, 2, 1), None), status=BidStatus.FUNDED)
        )

        assert funding.bid_status == BidStatus.FUNDED

    def test_get_bid_status_when_no_revisions(self) -> None:
        funding = SchemeFunding()

        assert funding.bid_status is None

    def test_get_financial_revisions_is_copy(self) -> None:
        funding = SchemeFunding()
        funding.update_financial(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_=FinancialType.FUNDING_ALLOCATION,
                amount=100_000,
                source=DataSource.ATF4_BID,
            )
        )

        funding.financial_revisions.clear()

        assert funding.financial_revisions

    def test_update_financial(self) -> None:
        funding = SchemeFunding()
        financial_revision = FinancialRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1), None),
            type_=FinancialType.FUNDING_ALLOCATION,
            amount=100_000,
            source=DataSource.ATF4_BID,
        )

        funding.update_financial(financial_revision)

        assert funding.financial_revisions == [financial_revision]

    def test_cannot_update_financial_with_another_current_spent_to_date(self) -> None:
        funding = SchemeFunding()
        financial_revision = FinancialRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1), None),
            type_=FinancialType.SPENT_TO_DATE,
            amount=100_000,
            source=DataSource.ATF4_BID,
        )
        funding.update_financial(financial_revision)

        with pytest.raises(
            ValueError, match=re.escape(f"Current spent to date already exists: {repr(financial_revision)}")
        ):
            funding.update_financial(
                FinancialRevision(
                    id_=2,
                    effective=DateRange(datetime(2020, 1, 1), None),
                    type_=FinancialType.SPENT_TO_DATE,
                    amount=200_000,
                    source=DataSource.ATF4_BID,
                )
            )

    def test_update_financials(self) -> None:
        funding = SchemeFunding()
        financial_revision1 = FinancialRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1), None),
            type_=FinancialType.FUNDING_ALLOCATION,
            amount=100_000,
            source=DataSource.ATF4_BID,
        )
        financial_revision2 = FinancialRevision(
            id_=2,
            effective=DateRange(datetime(2020, 1, 1), None),
            type_=FinancialType.EXPECTED_COST,
            amount=200_000,
            source=DataSource.ATF4_BID,
        )

        funding.update_financials(financial_revision1, financial_revision2)

        assert funding.financial_revisions == [financial_revision1, financial_revision2]

    def test_update_spend_to_date_closes_current_revision(self) -> None:
        funding = SchemeFunding()
        funding.update_financial(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1, 12), None),
                type_=FinancialType.SPENT_TO_DATE,
                amount=50_000,
                source=DataSource.ATF4_BID,
            )
        )

        funding.update_spend_to_date(now=datetime(2020, 2, 1, 13), amount=60_000)

        financial_revision = funding.financial_revisions[0]
        assert financial_revision.id == 1 and financial_revision.effective.date_to == datetime(2020, 2, 1, 13)

    def test_update_spend_to_date_adds_new_revision(self) -> None:
        funding = SchemeFunding()

        funding.update_spend_to_date(now=datetime(2020, 2, 1, 13), amount=60_000)

        financial_revision = funding.financial_revisions[0]
        assert (
            financial_revision.id is None
            and financial_revision.effective == DateRange(datetime(2020, 2, 1, 13), None)
            and financial_revision.type == FinancialType.SPENT_TO_DATE
            and financial_revision.amount == 60_000
            and financial_revision.source == DataSource.AUTHORITY_UPDATE
        )

    def test_get_funding_allocation_sums_amounts(self) -> None:
        funding = SchemeFunding()
        funding.update_financials(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_=FinancialType.FUNDING_ALLOCATION,
                amount=100_000,
                source=DataSource.ATF4_BID,
            ),
            FinancialRevision(
                id_=2,
                effective=DateRange(datetime(2020, 2, 1), None),
                type_=FinancialType.FUNDING_ALLOCATION,
                amount=20_000,
                source=DataSource.CHANGE_CONTROL,
            ),
        )

        assert funding.funding_allocation == 120_000

    def test_get_funding_allocation_selects_financial_type(self) -> None:
        funding = SchemeFunding()
        funding.update_financials(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_=FinancialType.FUNDING_ALLOCATION,
                amount=100_000,
                source=DataSource.ATF4_BID,
            ),
            FinancialRevision(
                id_=2,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_=FinancialType.EXPECTED_COST,
                amount=200_000,
                source=DataSource.ATF4_BID,
            ),
        )

        assert funding.funding_allocation == 100_000

    def test_get_funding_allocation_selects_latest_revision(self) -> None:
        funding = SchemeFunding()
        funding.update_financials(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), datetime(2020, 2, 1)),
                type_=FinancialType.FUNDING_ALLOCATION,
                amount=100_000,
                source=DataSource.ATF4_BID,
            ),
            FinancialRevision(
                id_=2,
                effective=DateRange(datetime(2020, 2, 1), None),
                type_=FinancialType.FUNDING_ALLOCATION,
                amount=200_000,
                source=DataSource.ATF4_BID,
            ),
        )

        assert funding.funding_allocation == 200_000

    def test_get_funding_allocation_when_no_matching_revisions(self) -> None:
        funding = SchemeFunding()
        funding.update_financial(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_=FinancialType.EXPECTED_COST,
                amount=100_000,
                source=DataSource.ATF4_BID,
            )
        )

        assert funding.funding_allocation is None

    def test_get_funding_allocation_when_no_revisions(self) -> None:
        funding = SchemeFunding()

        assert funding.funding_allocation is None

    def test_get_spend_to_date(self) -> None:
        funding = SchemeFunding()
        funding.update_financial(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_=FinancialType.SPENT_TO_DATE,
                amount=100_000,
                source=DataSource.ATF4_BID,
            )
        )

        assert funding.spend_to_date == 100_000

    def test_get_spend_to_date_selects_financial_type(self) -> None:
        funding = SchemeFunding()
        funding.update_financials(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_=FinancialType.SPENT_TO_DATE,
                amount=100_000,
                source=DataSource.ATF4_BID,
            ),
            FinancialRevision(
                id_=2,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_=FinancialType.EXPECTED_COST,
                amount=200_000,
                source=DataSource.ATF4_BID,
            ),
        )

        assert funding.spend_to_date == 100_000

    def test_get_spend_to_date_selects_latest_revision(self) -> None:
        funding = SchemeFunding()
        funding.update_financials(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), datetime(2020, 2, 1)),
                type_=FinancialType.SPENT_TO_DATE,
                amount=100_000,
                source=DataSource.ATF4_BID,
            ),
            FinancialRevision(
                id_=2,
                effective=DateRange(datetime(2020, 2, 1), None),
                type_=FinancialType.SPENT_TO_DATE,
                amount=200_000,
                source=DataSource.ATF4_BID,
            ),
        )

        assert funding.spend_to_date == 200_000

    def test_get_spend_to_date_when_no_matching_revisions(self) -> None:
        funding = SchemeFunding()
        funding.update_financial(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_=FinancialType.EXPECTED_COST,
                amount=100_000,
                source=DataSource.ATF4_BID,
            )
        )

        assert funding.spend_to_date is None

    def test_get_spend_to_date_when_no_revisions(self) -> None:
        funding = SchemeFunding()

        assert funding.spend_to_date is None

    def test_get_allocation_still_to_spend(self) -> None:
        funding = SchemeFunding()
        funding.update_financials(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_=FinancialType.FUNDING_ALLOCATION,
                amount=100_000,
                source=DataSource.ATF4_BID,
            ),
            FinancialRevision(
                id_=2,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_=FinancialType.SPENT_TO_DATE,
                amount=50_000,
                source=DataSource.ATF4_BID,
            ),
        )

        assert funding.allocation_still_to_spend == 50_000

    def test_get_allocation_still_to_spend_when_no_funding_allocation(self) -> None:
        funding = SchemeFunding()
        funding.update_financials(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_=FinancialType.SPENT_TO_DATE,
                amount=50_000,
                source=DataSource.ATF4_BID,
            )
        )

        assert funding.allocation_still_to_spend == -50_000

    def test_get_allocation_still_to_spend_when_no_spend_to_date(self) -> None:
        funding = SchemeFunding()
        funding.update_financials(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_=FinancialType.FUNDING_ALLOCATION,
                amount=100_000,
                source=DataSource.ATF4_BID,
            )
        )

        assert funding.allocation_still_to_spend == 100_000

    def test_get_allocation_still_to_spend_when_no_revisions(self) -> None:
        funding = SchemeFunding()

        assert funding.allocation_still_to_spend == 0


class TestBidStatusRevision:
    def test_create(self) -> None:
        bid_status_revision = BidStatusRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1), None),
            status=BidStatus.FUNDED,
        )

        assert (
            bid_status_revision.id == 1
            and bid_status_revision.effective == DateRange(datetime(2020, 1, 1), None)
            and bid_status_revision.status == BidStatus.FUNDED
        )


class TestFinancialRevision:
    def test_create(self) -> None:
        financial_revision = FinancialRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1), None),
            type_=FinancialType.FUNDING_ALLOCATION,
            amount=100_000,
            source=DataSource.ATF4_BID,
        )

        assert (
            financial_revision.id == 1
            and financial_revision.effective == DateRange(datetime(2020, 1, 1), None)
            and financial_revision.type == FinancialType.FUNDING_ALLOCATION
            and financial_revision.amount == 100_000
            and financial_revision.source == DataSource.ATF4_BID
        )

    @pytest.mark.parametrize(
        "effective_date_to, type_, expected",
        [
            (None, FinancialType.FUNDING_ALLOCATION, True),
            (datetime(2000, 2, 1), FinancialType.FUNDING_ALLOCATION, False),
            (None, FinancialType.SPENT_TO_DATE, False),
        ],
    )
    def test_is_current_funding_allocation(
        self, effective_date_to: datetime, type_: FinancialType, expected: bool
    ) -> None:
        financial_revision = FinancialRevision(
            id_=1,
            effective=DateRange(datetime(2000, 1, 1), effective_date_to),
            type_=type_,
            amount=0,
            source=DataSource.ATF4_BID,
        )

        assert financial_revision.is_current_funding_allocation == expected

    @pytest.mark.parametrize(
        "effective_date_to, type_, expected",
        [
            (None, FinancialType.SPENT_TO_DATE, True),
            (datetime(2000, 2, 1), FinancialType.SPENT_TO_DATE, False),
            (None, FinancialType.FUNDING_ALLOCATION, False),
        ],
    )
    def test_is_current_spent_to_date(self, effective_date_to: datetime, type_: FinancialType, expected: bool) -> None:
        financial_revision = FinancialRevision(
            id_=1,
            effective=DateRange(datetime(2000, 1, 1), effective_date_to),
            type_=type_,
            amount=0,
            source=DataSource.ATF4_BID,
        )

        assert financial_revision.is_current_spent_to_date == expected
