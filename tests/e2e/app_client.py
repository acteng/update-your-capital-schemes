import requests


class AppClient:
    DEFAULT_TIMEOUT = 10

    def __init__(self, url: str, api_key: str):
        self._url = url
        self._api_key = api_key

    def add_user(self, email: str) -> None:
        users = [{"email": email}]
        response = requests.post(
            f"{self._url}/users",
            headers={"Authorization": f"API-Key {self._api_key}"},
            json=users,
            timeout=self.DEFAULT_TIMEOUT,
        )
        assert response.status_code == 201

    def clear_users(self) -> None:
        response = requests.delete(
            f"{self._url}/users", headers={"Authorization": f"API-Key {self._api_key}"}, timeout=self.DEFAULT_TIMEOUT
        )
        assert response.status_code == 204
