import time
from dataclasses import dataclass
from typing import Any

from authlib.jose.rfc7517.base_key import Key
from authlib.oauth2.rfc6749.authorization_server import AuthorizationServer
from authlib.oauth2.rfc6749.grants import AuthorizationCodeGrant
from authlib.oauth2.rfc6749.requests import OAuth2Request
from authlib.oidc.core import UserInfo
from authlib.oidc.core.grants import OpenIDCode
from authlib.oidc.core.models import AuthorizationCodeMixin

from tests.e2e.oidc_server.clients import StubClient
from tests.e2e.oidc_server.jwts import PrivateKeyJwtClientAssertion
from tests.e2e.oidc_server.users import StubUser, UserRepository


@dataclass
class StubAuthorizationCode(AuthorizationCodeMixin):  # type: ignore
    code: str
    client_id: str
    redirect_uri: str
    scope: str
    user_id: str
    nonce: str
    auth_time: int = int(time.time())

    def get_redirect_uri(self) -> str:
        return self.redirect_uri

    def get_scope(self) -> str:
        return self.scope

    def get_nonce(self) -> str:
        return self.nonce

    def get_auth_time(self) -> int:
        return self.auth_time


class AuthorizationCodeRepository:
    def __init__(self) -> None:
        self._codes: dict[str, StubAuthorizationCode] = {}

    def add(self, code: StubAuthorizationCode) -> None:
        key = self._key(code.client_id, code.code)
        self._codes[key] = code

    def get_by_code(self, client_id: str, code: str) -> StubAuthorizationCode | None:
        return self._codes.get(self._key(client_id, code))

    def get_by_nonce(self, client_id: str, nonce: str) -> StubAuthorizationCode | None:
        return next(
            (code for code in self._codes.values() if code.client_id == client_id and code.nonce == nonce), None
        )

    def delete(self, code: StubAuthorizationCode) -> None:
        key = self._key(code.client_id, code.code)
        self._codes.pop(key)

    def _key(self, client_id: str, code: str) -> str:
        return f"{client_id}-{code}"


class StubAuthorizationCodeGrant(AuthorizationCodeGrant):  # type: ignore
    TOKEN_ENDPOINT_AUTH_METHODS = [PrivateKeyJwtClientAssertion.CLIENT_AUTH_METHOD]

    def __init__(self, request: OAuth2Request, server: AuthorizationServer) -> None:
        super().__init__(request, server)
        # attributes set by grant extension as initializer arguments are fixed
        self.users = UserRepository()
        self.authorization_codes = AuthorizationCodeRepository()

    def save_authorization_code(self, code: str, request: OAuth2Request) -> None:
        client = request.client
        self.authorization_codes.add(
            StubAuthorizationCode(
                code=code,
                client_id=client.client_id,
                redirect_uri=request.redirect_uri,
                scope=request.scope,
                user_id=request.user.id,
                nonce=request.data.get("nonce"),
            )
        )

    def query_authorization_code(self, code: str, client: StubClient) -> StubAuthorizationCode | None:
        return self.authorization_codes.get_by_code(client.client_id, code)

    def delete_authorization_code(self, authorization_code: StubAuthorizationCode) -> None:
        self.authorization_codes.delete(authorization_code)

    def authenticate_user(self, authorization_code: StubAuthorizationCode) -> StubUser:
        return self.users.get(authorization_code.user_id)


class StubUserInfo(UserInfo):  # type: ignore
    def __init__(self, user: StubUser) -> None:
        super().__init__(sub=user.id, email=user.email)


class StubOpenIDCode(OpenIDCode):  # type: ignore
    def __init__(
        self, issuer: str, key: Key, authorization_codes: AuthorizationCodeRepository, require_nonce: bool = False
    ) -> None:
        super().__init__(require_nonce)
        self._issuer = issuer
        self._key = key
        self._authorization_codes = authorization_codes

    def get_jwt_config(self, grant: AuthorizationCodeGrant) -> dict[str, Any]:
        return {"key": self._key.as_dict(is_private=True), "alg": "RS256", "iss": self._issuer, "exp": 3600}

    def exists_nonce(self, nonce: str, request: OAuth2Request) -> bool:
        return bool(self._authorization_codes.get_by_nonce(request.client_id, nonce))

    def generate_user_info(self, user: StubUser, scope: str) -> StubUserInfo:
        return StubUserInfo(user)
