from typing import Iterator, cast

import respx
from httpx import Response
from respx import Route


class StubAuthorizationServer:
    def __init__(self, resource_server_identifier: str, client_id: str, client_secret: str) -> None:
        self._url = "https://identity.example"
        self._resource_server_identifier = resource_server_identifier
        self._client_id = client_id
        self._client_secret = client_secret

    @property
    def configuration_endpoint(self) -> str:
        return f"{self._url}/.well-known/openid-configuration"

    @property
    def token_endpoint(self) -> str:
        return f"{self._url}/token"

    def given_configuration_endpoint_returns_configuration(self) -> None:
        respx.get(self.configuration_endpoint).mock(
            return_value=Response(200, json={"token_endpoint": self.token_endpoint})
        )

    def given_token_endpoint_returns_access_token(self, access_token: str, expires_in: int) -> Route:
        # Support multiple method calls to mock different responses
        route = respx.pop("token_endpoint", default=None)
        side_effects = list(cast(Iterator[Response], route.side_effect)) if route else []

        return respx.post(
            self.token_endpoint,
            name="token_endpoint",
            data={
                "grant_type": "client_credentials",
                "audience": self._resource_server_identifier,
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            },
        ).mock(
            side_effect=side_effects + [Response(200, json={"access_token": access_token, "expires_in": expires_in})]
        )
