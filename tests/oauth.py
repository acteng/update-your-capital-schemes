import responses
from responses.matchers import urlencoded_params_matcher


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
        responses.get(self.configuration_endpoint, json={"token_endpoint": self.token_endpoint})

    def given_token_endpoint_returns_access_token(self, access_token: str, expires_in: int) -> None:
        responses.post(
            self.token_endpoint,
            match=[
                urlencoded_params_matcher(
                    {
                        "grant_type": "client_credentials",
                        "audience": self._resource_server_identifier,
                        "client_id": self._client_id,
                        "client_secret": self._client_secret,
                    }
                )
            ],
            json={"access_token": access_token, "expires_in": expires_in},
        )
