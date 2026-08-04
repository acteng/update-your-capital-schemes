from collections.abc import Sequence

from authlib.oauth2.rfc6749 import ClientCredentialsGrant

from tests.e2e.oauth_server.jwts import PrivateKeyJwtClientAssertion


class PrivateKeyJwtClientCredentialsGrant(ClientCredentialsGrant):  # type: ignore
    TOKEN_ENDPOINT_AUTH_METHODS: Sequence[str] = [PrivateKeyJwtClientAssertion.CLIENT_AUTH_METHOD]
