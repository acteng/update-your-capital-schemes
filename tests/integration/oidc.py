from __future__ import annotations

from time import time
from types import TracebackType
from typing import Any, Callable, Type

from authlib.jose import JsonWebKey, jwt
from authlib.oauth2 import OAuth2Client
from authlib.oauth2.rfc6749 import OAuth2Token
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)
from requests.sessions import default_headers


def _generate_key_pair() -> tuple[bytes, bytes]:
    key_pair = rsa.generate_private_key(backend=default_backend(), public_exponent=65537, key_size=2048)
    private_key = key_pair.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
    public_key = key_pair.public_key().public_bytes(Encoding.OpenSSH, PublicFormat.OpenSSH)
    return private_key, public_key


class StubOAuth2Client(OAuth2Client):  # type: ignore
    issuer = "https://stub.example/"
    _subject = "stub_subject"
    nonce: str | None = None
    _key_id = "stub_key"
    _private_key, _public_key = _generate_key_pair()

    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        token_endpoint_auth_method: str | None = None,
        revocation_endpoint_auth_method: str | None = None,
        scope: str | None = None,
        state: str | None = None,
        redirect_uri: str | None = None,
        code_challenge_method: str | None = None,
        token: dict[str, Any] | None = None,
        token_placement: str = "header",
        update_token: Callable[[OAuth2Token], None] | None = None,
        **metadata: Any,
    ):
        super().__init__(
            None,
            client_id,
            client_secret,
            token_endpoint_auth_method,
            revocation_endpoint_auth_method,
            scope,
            state,
            redirect_uri,
            code_challenge_method,
            token,
            token_placement,
            update_token,
            **metadata,
        )
        self.headers = default_headers()

    def fetch_token(
        self,
        url: str | None = None,
        body: str = "",
        method: str = "POST",
        headers: dict[str, str] | None = None,
        auth: tuple[str, str] | None = None,
        grant_type: str | None = None,
        state: str | None = None,
        **kwargs: Any,
    ) -> OAuth2Token:
        issued_at = time()

        header = {
            "kid": self._key_id,
            "alg": "RS256",
        }

        payload = {
            "iss": self.issuer,
            "sub": self._subject,
            "aud": self.client_id,
            "exp": int(issued_at + 60),
            "iat": issued_at,
            "nonce": self.nonce,
        }

        id_token = jwt.encode(header, payload, self._private_key)

        return OAuth2Token({"id_token": id_token})

    @classmethod
    def key_set(cls) -> dict[str, Any]:
        key = JsonWebKey.import_key(cls._public_key, {"kty": "RSA", "kid": cls._key_id})
        return {"keys": [key.as_dict()]}

    def __enter__(self) -> StubOAuth2Client:
        return self

    def __exit__(
        self, exc_type: Type[BaseException] | None, exc_value: BaseException | None, traceback: TracebackType | None
    ) -> None:
        pass
