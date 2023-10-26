from __future__ import annotations

from dataclasses import dataclass

import requests


class AppClient:
    DEFAULT_TIMEOUT = 10

    def __init__(self, url: str, api_key: str):
        self._url = url
        self._api_key = api_key

    def add_user(self, user: UserRepr) -> None:
        response = requests.post(
            f"{self._url}/users",
            headers={"Authorization": f"API-Key {self._api_key}"},
            json=[user.__dict__],
            timeout=self.DEFAULT_TIMEOUT,
        )
        assert response.status_code == 201

    def clear_users(self) -> None:
        response = requests.delete(
            f"{self._url}/users", headers={"Authorization": f"API-Key {self._api_key}"}, timeout=self.DEFAULT_TIMEOUT
        )
        assert response.status_code == 204


@dataclass
class UserRepr:
    email: str
