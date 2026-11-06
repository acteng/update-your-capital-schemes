from schemes.domain.schemes.data_sources import DataSource


class SchemeFunding:
    def __init__(self, amount: int, source: DataSource):
        self._amount = amount
        self._source = source

    @property
    def amount(self) -> int:
        return self._amount

    @property
    def source(self) -> DataSource:
        return self._source


class SchemeSpend:
    # TODO: domain identifier should be mandatory for transient instances
    def __init__(self, id_: int | None, amount: int, source: DataSource):
        self._id = id_
        self._amount = amount
        self._source = source

    @property
    def id(self) -> int | None:
        return self._id

    @property
    def amount(self) -> int:
        return self._amount

    @property
    def source(self) -> DataSource:
        return self._source


class SchemeFinancials:
    def __init__(self) -> None:
        self._fundings: list[SchemeFunding] = []
        self._spend: SchemeSpend | None = None

    @property
    def fundings(self) -> list[SchemeFunding]:
        return list(self._fundings)

    @property
    def spend(self) -> SchemeSpend | None:
        return self._spend

    def update_funding(self, funding: SchemeFunding) -> None:
        self._fundings.append(funding)

    def update_fundings(self, *fundings: SchemeFunding) -> None:
        for financial in fundings:
            self.update_funding(financial)

    def update_spend(self, spend: SchemeSpend) -> None:
        self._spend = spend

    def update_spend_to_date(self, amount: int) -> None:
        self.update_spend(SchemeSpend(id_=None, amount=amount, source=DataSource.AUTHORITY_UPDATE))

    @property
    def funding_allocation(self) -> int | None:
        amounts = [funding.amount for funding in self.fundings]
        return sum(amounts) if amounts else None

    @property
    def spend_to_date(self) -> int | None:
        spend = self.spend
        return spend.amount if spend else None

    @property
    def allocation_still_to_spend(self) -> int:
        funding_allocation = self.funding_allocation or 0
        spend_to_date = self.spend_to_date or 0
        return funding_allocation - spend_to_date
