from authlib.oauth2 import OAuth2Error, OAuth2Request
from authlib.oauth2.rfc7523 import JWTBearerClientAssertion

from tests.e2e.oauth_server.clients import StubClient


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

    def __init__(self, token_url: str, audience: str):
        super().__init__(token_url)
        self._audience = audience
        self._jtis = JtiRepository()

    def __call__(self, query_client: StubClient, request: OAuth2Request) -> StubClient:
        client: StubClient = super().__call__(query_client, request)
        self._validate_audience(request.payload.data.get("audience"))
        return client

    def _validate_audience(self, audience: str) -> None:
        if self._audience:
            if not audience:
                raise OAuth2Error("Missing audience")
            if self._audience != audience:
                raise OAuth2Error(f"Invalid audience: {audience}")

    def validate_jti(self, claims: dict[str, str], jti: str) -> bool:
        sub = claims["sub"]
        if self._jtis.has_jti(sub, jti):
            return False
        self._jtis.add_jti(sub, jti)
        return True

    def resolve_client_public_key(self, client: StubClient, headers: dict[str, str]) -> bytes:
        return client.public_key
