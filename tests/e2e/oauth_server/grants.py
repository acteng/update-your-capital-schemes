from authlib.oauth2 import AuthorizationServer, OAuth2Error, OAuth2Request
from authlib.oauth2.rfc6749 import ClientCredentialsGrant

from tests.e2e.oauth_server.jwts import PrivateKeyJwtClientAssertion


class PrivateKeyJwtClientCredentialsGrant(ClientCredentialsGrant):  # type: ignore
    TOKEN_ENDPOINT_AUTH_METHODS = [PrivateKeyJwtClientAssertion.CLIENT_AUTH_METHOD]

    def __init__(self, request: OAuth2Request, server: AuthorizationServer):
        super().__init__(request, server)
        # attributes set by grant extension as initializer arguments are fixed
        self.audience = None

    def validate_token_request(self) -> None:
        super().validate_token_request()

        # TODO: validate audience in client authentication method
        audience = self.request.payload.data.get("audience")
        if self.audience:
            if not audience:
                raise OAuth2Error("Missing audience")
            if self.audience != audience:
                raise OAuth2Error(f"Invalid audience: {audience}")
