from __future__ import annotations

from datetime import datetime
from enum import Enum, auto, unique

from schemes.domain.dates import DateRange
from schemes.domain.schemes.data_source import DataSource


class SchemeFunding:
    def __init__(self) -> None:
        self._bid_status_revisions: list[BidStatusRevision] = []
        self._financial_revisions: list[FinancialRevision] = []

    @property
    def bid_status_revisions(self) -> list[BidStatusRevision]:
        return list(self._bid_status_revisions)

    def update_bid_status(self, bid_status_revision: BidStatusRevision) -> None:
        if bid_status_revision.effective.date_to is None:
            self._ensure_no_current_bid_status()

        self._bid_status_revisions.append(bid_status_revision)

    def update_bid_statuses(self, *bid_status_revisions: BidStatusRevision) -> None:
        for bid_status_revision in bid_status_revisions:
            self.update_bid_status(bid_status_revision)

    def _ensure_no_current_bid_status(self) -> None:
        current_bid_status = self._current_bid_status()
        if current_bid_status:
            raise ValueError(f"Current bid status already exists: {current_bid_status}")

    @property
    def bid_status(self) -> BidStatus | None:
        current_bid_status = self._current_bid_status()
        return current_bid_status.status if current_bid_status else None

    def _current_bid_status(self) -> BidStatusRevision | None:
        return next((revision for revision in self.bid_status_revisions if revision.effective.date_to is None), None)

    @property
    def financial_revisions(self) -> list[FinancialRevision]:
        return list(self._financial_revisions)

    def update_financial(self, financial_revision: FinancialRevision) -> None:
        if financial_revision.is_current_funding_allocation:
            self._ensure_no_current_funding_allocation()

        if financial_revision.is_current_spent_to_date:
            self._ensure_no_current_spent_to_date()

        self._financial_revisions.append(financial_revision)

    def update_financials(self, *financial_revisions: FinancialRevision) -> None:
        for financial_revision in financial_revisions:
            self.update_financial(financial_revision)

    def _ensure_no_current_funding_allocation(self) -> None:
        current_funding_allocation = next(
            (revision for revision in self._financial_revisions if revision.is_current_funding_allocation), None
        )
        if current_funding_allocation:
            raise ValueError(f"Current funding allocation already exists: {current_funding_allocation}")

    def _ensure_no_current_spent_to_date(self) -> None:
        current_spent_to_date = self._current_spent_to_date
        if current_spent_to_date:
            raise ValueError(f"Current spent to date already exists: {current_spent_to_date}")

    @property
    def _current_spent_to_date(self) -> FinancialRevision | None:
        return next((revision for revision in self._financial_revisions if revision.is_current_spent_to_date), None)

    def update_spend_to_date(self, now: datetime, amount: int) -> None:
        current_spent_to_date = self._current_spent_to_date
        if current_spent_to_date:
            current_spent_to_date.effective = DateRange(current_spent_to_date.effective.date_from, now)

        self.update_financial(
            FinancialRevision(
                id_=None,
                effective=DateRange(now, None),
                type_=FinancialType.SPENT_TO_DATE,
                amount=amount,
                source=DataSource.AUTHORITY_UPDATE,
            )
        )

    @property
    def funding_allocation(self) -> int | None:
        amounts = (revision.amount for revision in self._financial_revisions if revision.is_current_funding_allocation)
        return next(amounts, None)

    @property
    def change_control_adjustment(self) -> int | None:
        amounts = [
            revision.amount
            for revision in self._financial_revisions
            if revision.type == FinancialType.FUNDING_ALLOCATION
            and revision.source == DataSource.CHANGE_CONTROL
            and revision.effective.date_to is None
        ]
        return sum(amounts) if amounts else None

    @property
    def spend_to_date(self) -> int | None:
        amounts = (revision.amount for revision in self._financial_revisions if revision.is_current_spent_to_date)
        return next(amounts, None)

    @property
    def adjusted_funding_allocation(self) -> int:
        funding_allocation = self.funding_allocation or 0
        change_control_adjustment = self.change_control_adjustment or 0
        return funding_allocation + change_control_adjustment

    @property
    def allocation_still_to_spend(self) -> int:
        spend_to_date = self.spend_to_date or 0
        return self.adjusted_funding_allocation - spend_to_date


class BidStatusRevision:
    # TODO: domain identifier should be mandatory for transient instances
    def __init__(self, id_: int | None, effective: DateRange, status: BidStatus):
        self.id = id_
        self.effective = effective
        self.status = status


@unique
class BidStatus(Enum):
    SUBMITTED = auto()
    FUNDED = auto()
    NOT_FUNDED = auto()
    SPLIT = auto()
    DELETED = auto()


class FinancialRevision:
    # TODO: domain identifier should be mandatory for transient instances
    def __init__(self, id_: int | None, effective: DateRange, type_: FinancialType, amount: int, source: DataSource):
        self.id = id_
        self.effective = effective
        self.type = type_
        self.amount = amount
        self.source = source

    @property
    def is_current_funding_allocation(self) -> bool:
        return (
            self.type == FinancialType.FUNDING_ALLOCATION
            and self.source != DataSource.CHANGE_CONTROL
            and self.effective.date_to is None
        )

    @property
    def is_current_spent_to_date(self) -> bool:
        return self.type == FinancialType.SPENT_TO_DATE and self.effective.date_to is None


@unique
class FinancialType(Enum):
    EXPECTED_COST = auto()
    ACTUAL_COST = auto()
    FUNDING_ALLOCATION = auto()
    SPENT_TO_DATE = auto()
    FUNDING_REQUEST = auto()
