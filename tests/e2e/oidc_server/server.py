import requests
from pytest_flask.live_server import LiveServer

from tests.e2e.oidc_server.clients import StubClient
from tests.e2e.oidc_server.users import StubUser


class OidcServer(LiveServer):  # type: ignore
    DEFAULT_TIMEOUT = 10

    def add_user(self, user: StubUser) -> None:
        response = requests.post(f"{self._get_url()}/users", json=user.__dict__, timeout=self.DEFAULT_TIMEOUT)
        assert response.status_code == 201

    def clear_users(self) -> None:
        response = requests.delete(f"{self._get_url()}/users", timeout=self.DEFAULT_TIMEOUT)
        assert response.status_code == 204

    def add_client(self, client: StubClient) -> None:
        response = requests.post(f"{self._get_url()}/clients", json=client.__dict__, timeout=self.DEFAULT_TIMEOUT)
        assert response.status_code == 201

    def _get_url(self) -> str:
        return f"http://{self.host}:{self.port}"
