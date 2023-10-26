from __future__ import annotations

from dataclasses import dataclass

import requests


class AppClient:
    DEFAULT_TIMEOUT = 10

    def __init__(self, url: str, api_key: str):
        self._url = url
        self._session = requests.Session()
        self._session.headers.update({"Authorization": f"API-Key {api_key}"})

    def add_users(self, *users: UserRepr) -> None:
        json = [user.__dict__ for user in users]
        response = self._session.post(f"{self._url}/users", json=json, timeout=self.DEFAULT_TIMEOUT)
        assert response.status_code == 201

    def clear_users(self) -> None:
        response = self._session.delete(f"{self._url}/users", timeout=self.DEFAULT_TIMEOUT)
        assert response.status_code == 204


@dataclass
class UserRepr:
    email: str
