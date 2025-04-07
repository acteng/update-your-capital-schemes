from dataclasses import dataclass

from authlib.oauth2.rfc6749.models import ClientMixin


@dataclass
class StubClient(ClientMixin):  # type: ignore
    client_id: str
    client_secret: str

    def get_client_id(self) -> str:
        return self.client_id

    def check_client_secret(self, client_secret: str) -> bool:
        return self.client_secret == client_secret

    def check_endpoint_auth_method(self, method: str, endpoint: str) -> bool:
        return endpoint == "token" and method == "client_secret_post"

    def check_grant_type(self, grant_type: str) -> bool:
        return grant_type == "client_credentials"


class ClientRepository:
    def __init__(self) -> None:
        self._clients: dict[str, StubClient] = {}

    def add(self, client: StubClient) -> None:
        self._clients[client.client_id] = client

    def get(self, client_id: str) -> StubClient:
        return self._clients[client_id]

    def clear(self) -> None:
        self._clients.clear()
