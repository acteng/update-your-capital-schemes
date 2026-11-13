from dataclasses import dataclass

from schemes.domain.schemes.data_sources import DataSource


@dataclass(frozen=True)
class FundingProgramme:
    code: str
    is_eligible_for_authority_update: bool


class FundingProgrammes:
    ATF2 = FundingProgramme("ATF2", True)
    ATF3 = FundingProgramme("ATF3", True)
    ATF4 = FundingProgramme("ATF4", True)
    ATF4E = FundingProgramme("ATF4e", True)
    ATF5 = FundingProgramme("ATF5", True)
    BUS = FundingProgramme("BUS", True)
    CATF = FundingProgramme("CATF", True)
    CON = FundingProgramme("CON", True)
    CRSTS = FundingProgramme("CRSTS", False)
    IST = FundingProgramme("IST", True)
    LUF1 = FundingProgramme("LUF1", False)
    LUF2 = FundingProgramme("LUF2", False)
    LUF3 = FundingProgramme("LUF3", False)
    MRN = FundingProgramme("MRN", False)
    NCN = FundingProgramme("NCN", True)
    OTH = FundingProgramme("OTH", False)


class SchemeFunding:
    def __init__(self, funding_programme: FundingProgramme, amount: int):
        self._funding_programme = funding_programme
        self._amount = amount

    @property
    def funding_programme(self) -> FundingProgramme:
        return self._funding_programme

    @property
    def amount(self) -> int:
        return self._amount


class SchemeSpend:
    def __init__(self, surrogate_id: int | None, amount: int, source: DataSource):
        self._surrogate_id = surrogate_id
        self._amount = amount
        self._source = source

    @property
    def surrogate_id(self) -> int | None:
        return self._surrogate_id

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
        self.update_spend(SchemeSpend(surrogate_id=None, amount=amount, source=DataSource.AUTHORITY_UPDATE))

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
