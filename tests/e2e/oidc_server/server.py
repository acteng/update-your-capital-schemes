import requests
from pytest_flask.live_server import LiveServer

from tests.e2e.oidc_server.clients import StubClient
from tests.e2e.oidc_server.users import StubUser


class OidcServer(LiveServer):  # type: ignore
    def add_user(self, user: StubUser) -> None:
        response = requests.post(f"{self._get_url()}/users", json={"id": user.id, "email": user.email}, timeout=10)
        assert response.status_code == 201

    def clear_users(self) -> None:
        response = requests.delete(f"{self._get_url()}/users", timeout=10)
        assert response.status_code == 204

    def _get_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    def add_client(self, client: StubClient) -> None:
        response = requests.post(
            f"{self._get_url()}/clients",
            json={
                "client_id": client.client_id,
                "redirect_uri": client.redirect_uri,
                "public_key": client.public_key,
                "scope": client.scope,
            },
            timeout=10,
        )
        assert response.status_code == 201
