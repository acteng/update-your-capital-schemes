from dataclasses import asdict

import requests

from tests.e2e.oidc_server.clients import StubClient
from tests.e2e.oidc_server.users import StubUser


class OidcClient:
    DEFAULT_TIMEOUT = 10

    def __init__(self, url: str):
        self._url = url

    def add_user(self, user: StubUser) -> None:
        response = requests.post(f"{self._url}/users", json=asdict(user), timeout=self.DEFAULT_TIMEOUT)
        assert response.status_code == 201

    def clear_users(self) -> None:
        response = requests.delete(f"{self._url}/users", timeout=self.DEFAULT_TIMEOUT)
        assert response.status_code == 204

    def add_client(self, client: StubClient) -> None:
        response = requests.post(f"{self._url}/clients", json=asdict(client), timeout=self.DEFAULT_TIMEOUT)
        assert response.status_code == 201

    def clear_clients(self) -> None:
        response = requests.delete(f"{self._url}/clients", timeout=self.DEFAULT_TIMEOUT)
        assert response.status_code == 204
