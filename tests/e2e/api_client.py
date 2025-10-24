from dataclasses import asdict, dataclass

import requests


@dataclass(frozen=True)
class CollectionModel[T]:
    items: list[T]


@dataclass(frozen=True)
class FundingProgrammeModel:
    code: str
    eligibleForAuthorityUpdate: bool


@dataclass(frozen=True)
class AuthorityModel:
    abbreviation: str
    fullName: str


@dataclass(frozen=True)
class CapitalSchemeOverviewModel:
    name: str
    bidSubmittingAuthority: str
    fundingProgramme: str
    type: str


@dataclass(frozen=True)
class CapitalSchemeBidStatusDetailsModel:
    bidStatus: str


@dataclass(frozen=True)
class CapitalSchemeFinancialModel:
    type: str
    amount: int
    source: str


@dataclass(frozen=True)
class CapitalSchemeMilestoneModel:
    milestone: str
    observationType: str
    statusDate: str


@dataclass(frozen=True)
class CapitalSchemeMilestonesModel(CollectionModel[CapitalSchemeMilestoneModel]):
    currentMilestone: str | None


@dataclass(frozen=True)
class CapitalSchemeOutputModel:
    type: str
    measure: str
    observationType: str
    value: str


@dataclass(frozen=True)
class CapitalSchemeAuthorityReviewModel:
    reviewDate: str


@dataclass(frozen=True)
class CapitalSchemeModel:
    reference: str
    overview: CapitalSchemeOverviewModel
    bidStatusDetails: CapitalSchemeBidStatusDetailsModel
    financials: CollectionModel[CapitalSchemeFinancialModel]
    milestones: CapitalSchemeMilestonesModel
    outputs: CollectionModel[CapitalSchemeOutputModel]
    authorityReview: CapitalSchemeAuthorityReviewModel | None


@dataclass(frozen=True)
class MilestoneModel:
    name: str
    active: bool
    complete: bool


class ApiClient:
    DEFAULT_TIMEOUT = 10

    def __init__(self, url: str):
        self._url = url
        self._session = requests.Session()

    @property
    def base_url(self) -> str:
        return self._url

    def add_funding_programmes(self, *funding_programmes: FundingProgrammeModel) -> None:
        json = [asdict(funding_programme) for funding_programme in funding_programmes]
        response = self._session.post(f"{self._url}/funding-programmes", json=json, timeout=self.DEFAULT_TIMEOUT)
        response.raise_for_status()

    def clear_funding_programmes(self) -> None:
        response = self._session.delete(f"{self._url}/funding-programmes", timeout=self.DEFAULT_TIMEOUT)
        response.raise_for_status()

    def add_authorities(self, *authorities: AuthorityModel) -> None:
        json = [asdict(authority) for authority in authorities]
        response = self._session.post(f"{self._url}/authorities", json=json, timeout=self.DEFAULT_TIMEOUT)
        response.raise_for_status()

    def clear_authorities(self) -> None:
        response = self._session.delete(f"{self._url}/authorities", timeout=self.DEFAULT_TIMEOUT)
        response.raise_for_status()

    def add_schemes(self, *capital_schemes: CapitalSchemeModel) -> None:
        json = [asdict(capital_scheme) for capital_scheme in capital_schemes]
        response = self._session.post(f"{self._url}/capital-schemes", json=json, timeout=self.DEFAULT_TIMEOUT)
        response.raise_for_status()

    def clear_schemes(self) -> None:
        response = self._session.delete(f"{self._url}/capital-schemes", timeout=self.DEFAULT_TIMEOUT)
        response.raise_for_status()

    def add_milestones(self, *milestones: MilestoneModel) -> None:
        json = [asdict(milestone) for milestone in milestones]
        response = self._session.post(
            f"{self._url}/capital-schemes/milestones", json=json, timeout=self.DEFAULT_TIMEOUT
        )
        response.raise_for_status()

    def clear_milestones(self) -> None:
        response = self._session.delete(f"{self._url}/capital-schemes/milestones", timeout=self.DEFAULT_TIMEOUT)
        response.raise_for_status()
