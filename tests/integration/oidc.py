from base64 import urlsafe_b64encode
from time import time
from typing import Any

import responses
from authlib.jose import JsonWebKey, jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat, PublicFormat


class StubOidcServer:
    def __init__(self, client_id: str) -> None:
        self._url = "https://stub.example"
        self._key_id = "stub_key"
        self._private_key, self._public_key = self._generate_key_pair()
        self._client_id = client_id

    @property
    def token_endpoint(self) -> str:
        return f"{self._url}/token"

    @property
    def userinfo_endpoint(self) -> str:
        return f"{self._url}/userinfo"

    def key_set(self) -> dict[str, Any]:
        key = JsonWebKey.import_key(self._public_key, {"kty": "RSA", "kid": self._key_id})
        return {"keys": [key.as_dict()]}

    def given_token_endpoint_returns_id_token(
        self,
        issuer: str | None = None,
        audience: str | None = None,
        expiration_time: int | None = None,
        issued_at: int | None = None,
        nonce: str | None = None,
        signature: bytes | None = None,
    ) -> str:
        access_token = "stub_access_token"
        subject = "stub_subject"
        now = int(time())

        header = {
            "kid": self._key_id,
            "alg": "RS256",
        }

        payload = {
            "iss": issuer or self._url,
            "sub": subject,
            "aud": audience or self._client_id,
            "exp": expiration_time or now + 60,
            "iat": issued_at or now,
            "nonce": nonce,
        }

        id_token: str = jwt.encode(header, payload, self._private_key).decode()

        if signature:
            id_token = self._replace_signature(id_token, signature)

        responses.post(self.token_endpoint, json={"access_token": access_token, "id_token": id_token})

        return id_token

    def given_token_endpoint_returns_error(self, error: str, error_description: str) -> None:
        responses.post(self.token_endpoint, json={"error": error, "error_description": error_description})

    def given_userinfo_endpoint_returns_claims(self, email: str) -> None:
        responses.get(self.userinfo_endpoint, json={"email": email})

    def given_userinfo_endpoint_returns_error(self, error: str, error_description: str) -> None:
        responses.get(self.userinfo_endpoint, status=401, json={"error": error, "error_description": error_description})

    @staticmethod
    def _generate_key_pair() -> tuple[bytes, bytes]:
        key_pair = rsa.generate_private_key(backend=default_backend(), public_exponent=65537, key_size=2048)
        private_key = key_pair.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
        public_key = key_pair.public_key().public_bytes(Encoding.OpenSSH, PublicFormat.OpenSSH)
        return private_key, public_key

    @staticmethod
    def _replace_signature(token: str, signature: bytes) -> str:
        header, body, _ = token.split(".")
        return ".".join([header, body, urlsafe_b64encode(signature).decode()])
