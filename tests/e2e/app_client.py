from pydantic import BaseModel
from requests import Session


class AuthorityRepr(BaseModel):
    abbreviation: str
    name: str


class UserRepr(BaseModel):
    email: str


class OverviewRevisionRepr(BaseModel):
    effective_date_from: str
    effective_date_to: str | None
    name: str
    authority_abbreviation: str
    type: str
    funding_programme: str
    id: int | None = None


class BidStatusRevisionRepr(BaseModel):
    effective_date_from: str
    effective_date_to: str | None
    status: str
    id: int | None = None


class FinancialRevisionRepr(BaseModel):
    effective_date_from: str
    effective_date_to: str | None
    type: str
    amount: int
    source: str
    id: int | None = None


class MilestoneRevisionRepr(BaseModel):
    effective_date_from: str
    effective_date_to: str | None
    milestone: str
    observation_type: str
    status_date: str
    source: str
    id: int | None = None


class OutputRevisionRepr(BaseModel):
    effective_date_from: str
    effective_date_to: str | None
    type: str
    measure: str
    value: str
    observation_type: str
    id: int | None = None


class AuthorityReviewRepr(BaseModel):
    review_date: str
    source: str
    id: int | None = None


class SchemeRepr(BaseModel):
    id: int
    reference: str
    overview_revisions: list[OverviewRevisionRepr]
    bid_status_revisions: list[BidStatusRevisionRepr]
    financial_revisions: list[FinancialRevisionRepr]
    milestone_revisions: list[MilestoneRevisionRepr]
    output_revisions: list[OutputRevisionRepr]
    authority_reviews: list[AuthorityReviewRepr]


class AppClient:
    DEFAULT_TIMEOUT = 10

    def __init__(self, url: str, api_key: str):
        self._url = url
        self._session = Session()
        self._session.headers.update({"Authorization": f"API-Key {api_key}"})

    def set_clock(self, now: str) -> None:
        response = self._session.put(f"{self._url}/clock", json=now)
        response.raise_for_status()

    def add_authorities(self, *authorities: AuthorityRepr) -> None:
        json = [authority.model_dump() for authority in authorities]
        response = self._session.post(f"{self._url}/authorities", json=json, timeout=self.DEFAULT_TIMEOUT)
        response.raise_for_status()

    def add_users(self, authority_abbreviation: str, *users: UserRepr) -> None:
        json = [user.model_dump() for user in users]
        response = self._session.post(
            f"{self._url}/authorities/{authority_abbreviation}/users", json=json, timeout=self.DEFAULT_TIMEOUT
        )
        response.raise_for_status()

    def add_schemes(self, *schemes: SchemeRepr) -> None:
        json = [scheme.model_dump() for scheme in schemes]
        response = self._session.post(f"{self._url}/schemes", json=json, timeout=self.DEFAULT_TIMEOUT)
        response.raise_for_status()

    def get_scheme(self, reference: str) -> SchemeRepr:
        response = self._session.get(
            f"{self._url}/schemes/{reference}", headers={"Accept": "application/json"}, timeout=self.DEFAULT_TIMEOUT
        )
        response.raise_for_status()
        return SchemeRepr.model_validate(response.json())

    def clear_authorities(self) -> None:
        response = self._session.delete(f"{self._url}/authorities", timeout=self.DEFAULT_TIMEOUT)
        response.raise_for_status()

    def clear_users(self) -> None:
        response = self._session.delete(f"{self._url}/users", timeout=self.DEFAULT_TIMEOUT)
        response.raise_for_status()

    def clear_schemes(self) -> None:
        response = self._session.delete(f"{self._url}/schemes", timeout=self.DEFAULT_TIMEOUT)
        response.raise_for_status()
