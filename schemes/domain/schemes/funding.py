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
        current_bid_status_revision = self._current_bid_status_revision()
        if current_bid_status_revision:
            raise ValueError(f"Current bid status already exists: {current_bid_status_revision}")

    @property
    def bid_status(self) -> BidStatus | None:
        current_bid_status_revision = self._current_bid_status_revision()
        return current_bid_status_revision.status if current_bid_status_revision else None

    def _current_bid_status_revision(self) -> BidStatusRevision | None:
        return next((revision for revision in self.bid_status_revisions if revision.effective.date_to is None), None)

    @property
    def financial_revisions(self) -> list[FinancialRevision]:
        return list(self._financial_revisions)

    def update_financial(self, financial_revision: FinancialRevision) -> None:
        if financial_revision.is_current_spend_to_date:
            self._ensure_no_current_spend_to_date()

        self._financial_revisions.append(financial_revision)

    def update_financials(self, *financial_revisions: FinancialRevision) -> None:
        for financial_revision in financial_revisions:
            self.update_financial(financial_revision)

    def _ensure_no_current_spend_to_date(self) -> None:
        current_spend_to_date = self._current_spend_to_date
        if current_spend_to_date:
            raise ValueError(f"Current spend to date already exists: {current_spend_to_date}")

    @property
    def _current_spend_to_date(self) -> FinancialRevision | None:
        return next((revision for revision in self._financial_revisions if revision.is_current_spend_to_date), None)

    def update_spend_to_date(self, now: datetime, amount: int) -> None:
        current_spend_to_date = self._current_spend_to_date
        if current_spend_to_date:
            current_spend_to_date.effective = DateRange(current_spend_to_date.effective.date_from, now)

        self.update_financial(
            FinancialRevision(
                id_=None,
                effective=DateRange(now, None),
                type_=FinancialType.SPEND_TO_DATE,
                amount=amount,
                source=DataSource.AUTHORITY_UPDATE,
            )
        )

    @property
    def funding_allocation(self) -> int | None:
        amounts = [
            revision.amount
            for revision in self._financial_revisions
            if revision.type == FinancialType.FUNDING_ALLOCATION and revision.is_current_funding_allocation
        ]
        return sum(amounts) if amounts else None

    @property
    def spend_to_date(self) -> int | None:
        amounts = (revision.amount for revision in self._financial_revisions if revision.is_current_spend_to_date)
        return next(amounts, None)

    @property
    def allocation_still_to_spend(self) -> int:
        funding_allocation = self.funding_allocation or 0
        spend_to_date = self.spend_to_date or 0
        return funding_allocation - spend_to_date


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
        return self.type == FinancialType.FUNDING_ALLOCATION and self.effective.date_to is None

    @property
    def is_current_spend_to_date(self) -> bool:
        return self.type == FinancialType.SPEND_TO_DATE and self.effective.date_to is None


@unique
class FinancialType(Enum):
    EXPECTED_COST = auto()
    ACTUAL_COST = auto()
    FUNDING_ALLOCATION = auto()
    SPEND_TO_DATE = auto()
    FUNDING_REQUEST = auto()
