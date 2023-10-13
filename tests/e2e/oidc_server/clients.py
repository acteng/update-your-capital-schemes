from dataclasses import dataclass

from authlib.oauth2.rfc6749.models import ClientMixin


@dataclass
class StubClient(ClientMixin):  # type: ignore
    client_id: str
    redirect_uri: str
    public_key: str
    scope: str

    def get_client_id(self) -> str:
        return self.client_id

    def get_default_redirect_uri(self) -> str:
        raise NotImplementedError()

    def get_allowed_scope(self, scope: str) -> str:
        allowed_scope = [s for s in scope.split() if s in self.scope]
        return " ".join(allowed_scope)

    def check_redirect_uri(self, redirect_uri: str) -> bool:
        return self.redirect_uri == redirect_uri

    def check_response_type(self, response_type: str) -> bool:
        return response_type == "code"

    def check_client_secret(self, client_secret: str) -> bool:
        raise NotImplementedError()

    def check_endpoint_auth_method(self, method: str, endpoint: str) -> bool:
        return endpoint == "token" and method == "private_key_jwt"

    def check_grant_type(self, grant_type: str) -> bool:
        return grant_type == "authorization_code"


class ClientRepository:
    def __init__(self) -> None:
        self._clients: dict[str, StubClient] = {}

    def add(self, client: StubClient) -> None:
        self._clients[client.client_id] = client

    def get(self, client_id: str) -> StubClient:
        return self._clients[client_id]

    def clear(self) -> None:
        self._clients.clear()
