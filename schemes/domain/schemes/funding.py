from datetime import datetime
from enum import Enum, auto, unique

from schemes.domain.dates import DateRange
from schemes.domain.schemes.data_sources import DataSource


@unique
class FinancialType(Enum):
    EXPECTED_COST = auto()
    ACTUAL_COST = auto()
    FUNDING_ALLOCATION = auto()
    SPEND_TO_DATE = auto()
    FUNDING_REQUEST = auto()


class FinancialRevision:
    # TODO: domain identifier should be mandatory for transient instances
    def __init__(self, id_: int | None, effective: DateRange, type_: FinancialType, amount: int, source: DataSource):
        self._id = id_
        self._effective = effective
        self._type = type_
        self._amount = amount
        self._source = source

    @property
    def id(self) -> int | None:
        return self._id

    @property
    def effective(self) -> DateRange:
        return self._effective

    @property
    def type(self) -> FinancialType:
        return self._type

    @property
    def amount(self) -> int:
        return self._amount

    @property
    def source(self) -> DataSource:
        return self._source

    @property
    def is_current_funding_allocation(self) -> bool:
        return self.type == FinancialType.FUNDING_ALLOCATION and self.effective.date_to is None

    @property
    def is_current_spend_to_date(self) -> bool:
        return self.type == FinancialType.SPEND_TO_DATE and self.effective.date_to is None

    def close(self, effective_date_to: datetime) -> None:
        self._effective = DateRange(self.effective.date_from, effective_date_to)


class SchemeFunding:
    def __init__(self) -> None:
        self._financial_revisions: list[FinancialRevision] = []

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
            current_spend_to_date.close(now)

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
