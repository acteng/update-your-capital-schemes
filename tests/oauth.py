from typing import Iterator, cast
from unittest.mock import ANY

from httpx import Response
from respx import MockRouter, Route


class StubAuthorizationServer:
    def __init__(
        self, respx_mock: MockRouter, resource_server_identifier: str, client_id: str, public_key: bytes
    ) -> None:
        self._respx_mock = respx_mock
        self._url = "https://identity.example"
        self._resource_server_identifier = resource_server_identifier
        self._client_id = client_id
        self._public_key = public_key

    @property
    def configuration_endpoint(self) -> str:
        return f"{self._url}/.well-known/openid-configuration"

    @property
    def token_endpoint(self) -> str:
        return f"{self._url}/token"

    def given_configuration_endpoint_returns_configuration(self) -> None:
        self._respx_mock.get(self.configuration_endpoint).respond(200, json={"token_endpoint": self.token_endpoint})

    def given_token_endpoint_returns_access_token(self, access_token: str, expires_in: int) -> Route:
        # Support multiple method calls to mock different responses
        route = self._respx_mock.pop("token_endpoint", default=None)
        side_effects = list(cast(Iterator[Response], route.side_effect)) if route else []

        return self._respx_mock.post(
            self.token_endpoint,
            name="token_endpoint",
            data={
                "grant_type": "client_credentials",
                "audience": self._resource_server_identifier,
                "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                # TODO: verify JWT (signed by public_key, iss=client_id, sub=client_id, aud=token_endpoint)
                "client_assertion": ANY,
            },
        ).mock(
            side_effect=side_effects + [Response(200, json={"access_token": access_token, "expires_in": expires_in})]
        )
