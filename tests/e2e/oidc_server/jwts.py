from authlib.oauth2.rfc7523 import JWTBearerClientAssertion

from tests.e2e.oidc_server.clients import StubClient


class JtiRepository:
    def __init__(self) -> None:
        self._keys: dict[str, bool] = {}

    def add_jti(self, sub: str, jti: str) -> None:
        self._keys[self._key(sub, jti)] = True

    def has_jti(self, sub: str, jti: str) -> bool:
        return self._key(sub, jti) in self._keys

    def _key(self, sub: str, jti: str) -> str:
        return f"{sub}-{jti}"


class PrivateKeyJwtClientAssertion(JWTBearerClientAssertion):  # type: ignore
    CLIENT_AUTH_METHOD = "private_key_jwt"

    def __init__(self, token_url: str, validate_jti: bool = True) -> None:
        super().__init__(token_url, validate_jti)
        self._jtis = JtiRepository()

    def validate_jti(self, claims: dict[str, str], jti: str) -> bool:
        sub = claims["sub"]
        if self._jtis.has_jti(sub, jti):
            return False
        self._jtis.add_jti(sub, jti)
        return True

    def resolve_client_public_key(self, client: StubClient, headers: dict[str, str]) -> str:
        return client.public_key
