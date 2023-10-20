from base64 import b64encode

import requests


class AppClient:
    DEFAULT_TIMEOUT = 10

    def __init__(self, url: str, username: str, password: str):
        self._url = url
        credentials = f"{username}:{password}"
        self._authorization = f"Basic {b64encode(credentials.encode()).decode()}"

    def add_user(self, email: str) -> None:
        users = [{"email": email}]
        response = requests.post(
            f"{self._url}/users",
            headers={"Authorization": self._authorization},
            json=users,
            timeout=self.DEFAULT_TIMEOUT,
        )
        assert response.status_code == 201

    def clear_users(self) -> None:
        response = requests.delete(
            f"{self._url}/users", headers={"Authorization": self._authorization}, timeout=self.DEFAULT_TIMEOUT
        )
        assert response.status_code == 204
