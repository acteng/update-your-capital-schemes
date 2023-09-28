from dataclasses import dataclass
from typing import Any

from authlib.oauth2.rfc6749.models import TokenMixin
from authlib.oauth2.rfc6750 import BearerTokenValidator

from tests.e2e.oidc_server.clients import StubClient


@dataclass
class StubToken(TokenMixin):  # type: ignore
    client_id: str
    user_id: str
    scope: str

    def check_client(self, client: StubClient) -> bool:
        raise NotImplementedError()

    def get_scope(self) -> str:
        return self.scope

    def get_expires_in(self) -> int:
        raise NotImplementedError()

    def is_expired(self) -> bool:
        return False

    def is_revoked(self) -> bool:
        return False


class TokenRepository:
    def __init__(self) -> None:
        self._tokens: dict[str, StubToken] = {}

    def get(self, access_token: str) -> StubToken:
        return self._tokens[access_token]

    def add(self, access_token: str, token: StubToken) -> None:
        self._tokens[access_token] = token


class StubBearerTokenValidator(BearerTokenValidator):  # type: ignore
    def __init__(self, tokens: TokenRepository, realm: str | None = None, **extra_attributes: Any) -> None:
        super().__init__(realm, **extra_attributes)
        self._tokens = tokens

    def authenticate_token(self, token_string: str) -> StubToken:
        return self._tokens.get(token_string)
