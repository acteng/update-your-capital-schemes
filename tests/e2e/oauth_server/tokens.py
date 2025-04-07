from typing import Any

from authlib.jose import KeySet
from authlib.oauth2.rfc6749 import ClientMixin
from authlib.oauth2.rfc9068 import JWTBearerTokenGenerator


class StubJWTBearerTokenGenerator(JWTBearerTokenGenerator):  # type: ignore
    def __init__(self, issuer: str, resource_server_identifier: str, jwks: KeySet):
        super().__init__(issuer)
        self._resource_server_identifier = resource_server_identifier
        self._jwks = jwks

    def get_jwks(self) -> KeySet:
        return self._jwks

    def get_audiences(self, client: ClientMixin, user: Any, scope: str) -> str | list[str]:
        return self._resource_server_identifier
