from dataclasses import asdict, dataclass

import requests


@dataclass(frozen=True)
class AuthorityModel:
    abbreviation: str
    fullName: str


class ApiClient:
    DEFAULT_TIMEOUT = 10

    def __init__(self, url: str):
        self._url = url
        self._session = requests.Session()

    def add_authorities(self, *authorities: AuthorityModel) -> None:
        json = [asdict(authority) for authority in authorities]
        response = self._session.post(f"{self._url}/authorities", json=json, timeout=self.DEFAULT_TIMEOUT)
        response.raise_for_status()

    def clear_authorities(self) -> None:
        response = self._session.delete(f"{self._url}/authorities", timeout=self.DEFAULT_TIMEOUT)
        response.raise_for_status()
