from typing import Any

from pydantic import BaseModel as pydantic_BaseModel
from pydantic import ConfigDict
from pydantic.alias_generators import to_camel
from requests import Session


class BaseModel(pydantic_BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    def to_json(self) -> dict[str, Any]:
        return self.model_dump(mode="json", by_alias=True)


class CollectionModel[T](BaseModel):
    items: list[T]


class FundingProgrammeModel(BaseModel):
    code: str
    eligible_for_authority_update: bool


class AuthorityModel(BaseModel):
    abbreviation: str
    full_name: str


class CapitalSchemeOverviewModel(BaseModel):
    name: str
    bid_submitting_authority: str
    funding_programme: str
    type: str


class CapitalSchemeBidStatusDetailsModel(BaseModel):
    bid_status: str


class CapitalSchemeFinancialModel(BaseModel):
    type: str
    amount: int
    source: str


class CapitalSchemeMilestoneModel(BaseModel):
    milestone: str
    observation_type: str
    status_date: str


class CapitalSchemeMilestonesModel(CollectionModel[CapitalSchemeMilestoneModel]):
    current_milestone: str | None


class CapitalSchemeOutputModel(BaseModel):
    type: str
    measure: str
    observation_type: str
    value: str


class CapitalSchemeAuthorityReviewModel(BaseModel):
    review_date: str


class CapitalSchemeModel(BaseModel):
    reference: str
    overview: CapitalSchemeOverviewModel
    bid_status_details: CapitalSchemeBidStatusDetailsModel
    financials: CollectionModel[CapitalSchemeFinancialModel]
    milestones: CapitalSchemeMilestonesModel
    outputs: CollectionModel[CapitalSchemeOutputModel]
    authority_review: CapitalSchemeAuthorityReviewModel | None


class MilestoneModel(BaseModel):
    name: str
    active: bool
    complete: bool


class ApiClient:
    DEFAULT_TIMEOUT = 10

    def __init__(self, url: str):
        self._url = url
        self._session = Session()

    @property
    def base_url(self) -> str:
        return self._url

    def add_funding_programmes(self, *funding_programmes: FundingProgrammeModel) -> None:
        json = [funding_programme.to_json() for funding_programme in funding_programmes]
        response = self._session.post(f"{self._url}/funding-programmes", json=json, timeout=self.DEFAULT_TIMEOUT)
        response.raise_for_status()

    def clear_funding_programmes(self) -> None:
        response = self._session.delete(f"{self._url}/funding-programmes", timeout=self.DEFAULT_TIMEOUT)
        response.raise_for_status()

    def add_authorities(self, *authorities: AuthorityModel) -> None:
        json = [authority.to_json() for authority in authorities]
        response = self._session.post(f"{self._url}/authorities", json=json, timeout=self.DEFAULT_TIMEOUT)
        response.raise_for_status()

    def clear_authorities(self) -> None:
        response = self._session.delete(f"{self._url}/authorities", timeout=self.DEFAULT_TIMEOUT)
        response.raise_for_status()

    def add_schemes(self, *capital_schemes: CapitalSchemeModel) -> None:
        json = [capital_scheme.to_json() for capital_scheme in capital_schemes]
        response = self._session.post(f"{self._url}/capital-schemes", json=json, timeout=self.DEFAULT_TIMEOUT)
        response.raise_for_status()

    def clear_schemes(self) -> None:
        response = self._session.delete(f"{self._url}/capital-schemes", timeout=self.DEFAULT_TIMEOUT)
        response.raise_for_status()

    def add_milestones(self, *milestones: MilestoneModel) -> None:
        json = [milestone.to_json() for milestone in milestones]
        response = self._session.post(
            f"{self._url}/capital-schemes/milestones", json=json, timeout=self.DEFAULT_TIMEOUT
        )
        response.raise_for_status()

    def clear_milestones(self) -> None:
        response = self._session.delete(f"{self._url}/capital-schemes/milestones", timeout=self.DEFAULT_TIMEOUT)
        response.raise_for_status()
