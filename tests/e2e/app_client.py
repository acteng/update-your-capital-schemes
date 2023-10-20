import requests


class AppClient:
    DEFAULT_TIMEOUT = 10

    def __init__(self, url: str):
        self._url = url

    def add_user(self, email: str) -> None:
        users = [{"email": email}]
        response = requests.post(f"{self._url}/users", json=users, timeout=self.DEFAULT_TIMEOUT)
        assert response.status_code == 201

    def clear_users(self) -> None:
        response = requests.delete(f"{self._url}/users", timeout=self.DEFAULT_TIMEOUT)
        assert response.status_code == 204
