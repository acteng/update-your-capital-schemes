import responses
from responses.matchers import urlencoded_params_matcher


class StubAuthorizationServer:
    def __init__(self, client_id: str, client_secret: str, resource_server_identifier: str):
        self._url = "https://auth.example"
        self._client_id = client_id
        self._client_secret = client_secret
        self._resource_server_identifier = resource_server_identifier

    @property
    def token_endpoint(self) -> str:
        return f"{self._url}/token"

    def given_token_endpoint_returns_access_token(self, access_token: str) -> None:
        responses.post(
            self.token_endpoint,
            match=[
                urlencoded_params_matcher(
                    {
                        "grant_type": "client_credentials",
                        "client_id": self._client_id,
                        "client_secret": self._client_secret,
                        "audience": self._resource_server_identifier,
                    }
                )
            ],
            json={"access_token": access_token},
        )
