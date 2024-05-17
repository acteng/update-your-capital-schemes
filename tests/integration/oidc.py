from __future__ import annotations

from time import time
from typing import Any

import responses
from authlib.jose import JsonWebKey, jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)


class StubOidcServer:
    def __init__(self, client_id: str) -> None:
        self._issuer = "https://stub.example/"
        self._key_id = "stub_key"
        self._private_key, self._public_key = self._generate_key_pair()
        self._client_id = client_id

    @property
    def token_endpoint(self) -> str:
        return f"{self._issuer}token"

    def key_set(self) -> dict[str, Any]:
        key = JsonWebKey.import_key(self._public_key, {"kty": "RSA", "kid": self._key_id})
        return {"keys": [key.as_dict()]}

    def given_token_endpoint_returns(
        self,
        issuer: str | None = None,
        audience: str | None = None,
        expiration_time: int | None = None,
        nonce: str | None = None,
    ) -> None:
        subject = "stub_subject"
        issued_at = time()

        header = {
            "kid": self._key_id,
            "alg": "RS256",
        }

        payload = {
            "iss": issuer or self._issuer,
            "sub": subject,
            "aud": audience or self._client_id,
            "exp": expiration_time or int(issued_at + 60),
            "iat": issued_at,
            "nonce": nonce,
        }

        id_token = jwt.encode(header, payload, self._private_key)

        responses.add(responses.POST, self.token_endpoint, json={"id_token": id_token.decode()})

    @staticmethod
    def _generate_key_pair() -> tuple[bytes, bytes]:
        key_pair = rsa.generate_private_key(backend=default_backend(), public_exponent=65537, key_size=2048)
        private_key = key_pair.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
        public_key = key_pair.public_key().public_bytes(Encoding.OpenSSH, PublicFormat.OpenSSH)
        return private_key, public_key
