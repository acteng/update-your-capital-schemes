from __future__ import annotations

from dataclasses import asdict, dataclass

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


@dataclass
class AuthorityRepr:
    id: int
    name: str


@dataclass
class UserRepr:
    email: str


@dataclass
class SchemeRepr:  # pylint:disable=duplicate-code
    id: int
    name: str
    type: str | None = None
    funding_programme: str | None = None
