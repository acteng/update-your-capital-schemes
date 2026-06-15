from pydantic import BaseModel
from requests import Session


class UserRepr(BaseModel):
    email: str


class AppClient:
    DEFAULT_TIMEOUT = 10

    def __init__(self, url: str, api_key: str):
        self._url = url
        self._session = Session()
        self._session.headers.update({"Authorization": f"API-Key {api_key}"})

    def set_clock(self, now: str) -> None:
        response = self._session.put(f"{self._url}/clock", json=now)
        response.raise_for_status()

    def add_users(self, authority_abbreviation: str, *users: UserRepr) -> None:
        json = [user.model_dump() for user in users]
        response = self._session.post(
            f"{self._url}/authorities/{authority_abbreviation}/users", json=json, timeout=self.DEFAULT_TIMEOUT
        )
        response.raise_for_status()

    def clear_users(self) -> None:
        response = self._session.delete(f"{self._url}/users", timeout=self.DEFAULT_TIMEOUT)
        response.raise_for_status()
