from __future__ import annotations

from dataclasses import asdict, dataclass, field

import requests


class AppClient:
    DEFAULT_TIMEOUT = 10

    def __init__(self, url: str, api_key: str):
        self._url = url
        self._session = requests.Session()
        self._session.headers.update({"Authorization": f"API-Key {api_key}"})

    def add_authorities(self, *authorities: AuthorityRepr) -> None:
        json = [asdict(authority) for authority in authorities]
        response = self._session.post(f"{self._url}/authorities", json=json, timeout=self.DEFAULT_TIMEOUT)
        assert response.status_code == 201

    def add_users(self, authority_id: int, *users: UserRepr) -> None:
        json = [asdict(user) for user in users]
        response = self._session.post(
            f"{self._url}/authorities/{authority_id}/users", json=json, timeout=self.DEFAULT_TIMEOUT
        )
        assert response.status_code == 201

    def add_schemes(self, authority_id: int, *schemes: SchemeRepr) -> None:
        json = [asdict(scheme) for scheme in schemes]
        response = self._session.post(
            f"{self._url}/authorities/{authority_id}/schemes", json=json, timeout=self.DEFAULT_TIMEOUT
        )
        assert response.status_code == 201

    def clear_authorities(self) -> None:
        response = self._session.delete(f"{self._url}/authorities", timeout=self.DEFAULT_TIMEOUT)
        assert response.status_code == 204

    def clear_users(self) -> None:
        response = self._session.delete(f"{self._url}/users", timeout=self.DEFAULT_TIMEOUT)
        assert response.status_code == 204

    def clear_schemes(self) -> None:
        response = self._session.delete(f"{self._url}/schemes", timeout=self.DEFAULT_TIMEOUT)
        assert response.status_code == 204


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
    milestone_revisions: list[MilestoneRevisionRepr] = field(default_factory=list)
    financial_revisions: list[FinancialRevisionRepr] = field(default_factory=list)
    output_revisions: list[OutputRevisionRepr] = field(default_factory=list)


@dataclass(frozen=True)
class MilestoneRevisionRepr:
    effective_date_from: str
    effective_date_to: str | None
    milestone: str
    observation_type: str
    status_date: str


@dataclass(frozen=True)
class FinancialRevisionRepr:
    id: int
    effective_date_from: str
    effective_date_to: str | None
    type: str
    amount: int
    source: str


@dataclass(frozen=True)
class OutputRevisionRepr:
    effective_date_from: str
    effective_date_to: str | None
    type: str
    measure: str
    value: str
    observation_type: str
