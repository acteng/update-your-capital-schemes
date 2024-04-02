from __future__ import annotations

from dataclasses import asdict, dataclass, field

import requests
from dataclass_wizard import fromdict


class AppClient:
    DEFAULT_TIMEOUT = 10

    def __init__(self, url: str, api_key: str):
        self._url = url
        self._session = requests.Session()
        self._session.headers.update({"Authorization": f"API-Key {api_key}"})

    def set_clock(self, now: str) -> None:
        response = self._session.put(f"{self._url}/clock", data={"now": now})
        response.raise_for_status()

    def add_authorities(self, *authorities: AuthorityRepr) -> None:
        json = [asdict(authority) for authority in authorities]
        response = self._session.post(f"{self._url}/authorities", json=json, timeout=self.DEFAULT_TIMEOUT)
        response.raise_for_status()

    def add_users(self, authority_id: int, *users: UserRepr) -> None:
        json = [asdict(user) for user in users]
        response = self._session.post(
            f"{self._url}/authorities/{authority_id}/users", json=json, timeout=self.DEFAULT_TIMEOUT
        )
        response.raise_for_status()

    def add_schemes(self, authority_id: int, *schemes: SchemeRepr) -> None:
        json = [asdict(scheme) for scheme in schemes]
        response = self._session.post(
            f"{self._url}/authorities/{authority_id}/schemes", json=json, timeout=self.DEFAULT_TIMEOUT
        )
        response.raise_for_status()

    def get_scheme(self, id_: int) -> SchemeRepr:
        response = self._session.get(
            f"{self._url}/schemes/{id_}", headers={"Accept": "application/json"}, timeout=self.DEFAULT_TIMEOUT
        )
        response.raise_for_status()
        scheme_repr: SchemeRepr = fromdict(SchemeRepr, response.json())
        return scheme_repr

    def clear_authorities(self) -> None:
        response = self._session.delete(f"{self._url}/authorities", timeout=self.DEFAULT_TIMEOUT)
        response.raise_for_status()

    def clear_users(self) -> None:
        response = self._session.delete(f"{self._url}/users", timeout=self.DEFAULT_TIMEOUT)
        response.raise_for_status()

    def clear_schemes(self) -> None:
        response = self._session.delete(f"{self._url}/schemes", timeout=self.DEFAULT_TIMEOUT)
        response.raise_for_status()


@dataclass(frozen=True)
class AuthorityRepr:
    id: int
    name: str


@dataclass(frozen=True)
class UserRepr:
    email: str


@dataclass(frozen=True)
class SchemeRepr:
    id: int
    name: str
    type: str | None = None
    funding_programme: str | None = None
    bid_status_revisions: list[BidStatusRevisionRepr] = field(default_factory=list)
    financial_revisions: list[FinancialRevisionRepr] = field(default_factory=list)
    milestone_revisions: list[MilestoneRevisionRepr] = field(default_factory=list)
    output_revisions: list[OutputRevisionRepr] = field(default_factory=list)
    authority_reviews: list[AuthorityReviewRepr] = field(default_factory=list)


@dataclass(frozen=True)
class BidStatusRevisionRepr:
    effective_date_from: str
    effective_date_to: str | None
    status: str
    id: int | None = None


@dataclass(frozen=True)
class FinancialRevisionRepr:
    effective_date_from: str
    effective_date_to: str | None
    type: str
    amount: int
    source: str
    id: int | None = None


@dataclass(frozen=True)
class MilestoneRevisionRepr:
    effective_date_from: str
    effective_date_to: str | None
    milestone: str
    observation_type: str
    status_date: str
    source: str
    id: int | None = None


@dataclass(frozen=True)
class OutputRevisionRepr:
    effective_date_from: str
    effective_date_to: str | None
    type: str
    measure: str
    value: str
    observation_type: str
    id: int | None = None


@dataclass(frozen=True)
class AuthorityReviewRepr:
    review_date: str
    source: str
    id: int | None = None
