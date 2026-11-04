from enum import Enum, auto, unique

from schemes.domain.schemes.data_sources import DataSource


@unique
class FinancialType(Enum):
    EXPECTED_COST = auto()
    ACTUAL_COST = auto()
    FUNDING_ALLOCATION = auto()
    SPEND_TO_DATE = auto()
    FUNDING_REQUEST = auto()


class SchemeFinancial:
    # TODO: domain identifier should be mandatory for transient instances
    def __init__(self, id_: int | None, type_: FinancialType, amount: int, source: DataSource):
        self._id = id_
        self._type = type_
        self._amount = amount
        self._source = source

    @property
    def id(self) -> int | None:
        return self._id

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
    def is_funding_allocation(self) -> bool:
        return self.type == FinancialType.FUNDING_ALLOCATION

    @property
    def is_spend_to_date(self) -> bool:
        return self.type == FinancialType.SPEND_TO_DATE


class SchemeFunding:
    def __init__(self) -> None:
        self._financials: list[SchemeFinancial] = []

    @property
    def financials(self) -> list[SchemeFinancial]:
        return list(self._financials)

    def update_financial(self, financial: SchemeFinancial) -> None:
        if financial.is_spend_to_date:
            self._ensure_no_spend_to_date()

        self._financials.append(financial)

    def update_financials(self, *financials: SchemeFinancial) -> None:
        for financial in financials:
            self.update_financial(financial)

    def _ensure_no_spend_to_date(self) -> None:
        spend_to_date = self._spend_to_date
        if spend_to_date:
            raise ValueError(f"Spend to date already exists: {spend_to_date}")

    @property
    def _spend_to_date(self) -> SchemeFinancial | None:
        return next((financial for financial in self._financials if financial.is_spend_to_date), None)

    def update_spend_to_date(self, amount: int) -> None:
        spend_to_date = self._spend_to_date
        if spend_to_date:
            self._financials.remove(spend_to_date)

        self.update_financial(
            SchemeFinancial(
                id_=None, type_=FinancialType.SPEND_TO_DATE, amount=amount, source=DataSource.AUTHORITY_UPDATE
            )
        )

    @property
    def funding_allocation(self) -> int | None:
        amounts = [financial.amount for financial in self._financials if financial.is_funding_allocation]
        return sum(amounts) if amounts else None

    @property
    def spend_to_date(self) -> int | None:
        amounts = (financial.amount for financial in self._financials if financial.is_spend_to_date)
        return next(amounts, None)

    @property
    def allocation_still_to_spend(self) -> int:
        funding_allocation = self.funding_allocation or 0
        spend_to_date = self.spend_to_date or 0
        return funding_allocation - spend_to_date
