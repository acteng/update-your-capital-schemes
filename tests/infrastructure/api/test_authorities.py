import pytest
import responses
from authlib.integrations.flask_client import FlaskIntegration, FlaskOAuth2App
from responses.matchers import header_matcher

from schemes.infrastructure.api.authorities import ApiAuthorityRepository
from tests.infrastructure.api.oauth import StubAuthorizationServer


class TestApiAuthorityRepository:
    @pytest.fixture(name="authorization_server")
    def authorization_server_fixture(self) -> StubAuthorizationServer:
        return StubAuthorizationServer(
            client_id="stub_client_id",
            client_secret="stub_client_secret",
            resource_server_identifier="https://api.example",
        )

    @pytest.fixture(name="authorities")
    def authorities_fixture(self, authorization_server: StubAuthorizationServer) -> ApiAuthorityRepository:
        remote_app = FlaskOAuth2App(
            FlaskIntegration("ate"),
            client_id="stub_client_id",
            client_secret="stub_client_secret",
            access_token_url=authorization_server.token_endpoint,
            access_token_params={"audience": "https://api.example"},
            api_base_url="https://api.example",
            client_kwargs={"token_endpoint_auth_method": "client_secret_post"},
        )
        return ApiAuthorityRepository(remote_app)

    @responses.activate
    def test_get_authority(
        self, authorization_server: StubAuthorizationServer, authorities: ApiAuthorityRepository
    ) -> None:
        authorization_server.given_token_endpoint_returns_access_token("dummy_jwt")
        responses.get(
            "https://api.example/authorities/LIV",
            match=[header_matcher({"Authorization": "Bearer dummy_jwt"})],
            json={"abbreviation": "LIV", "fullName": "Liverpool City Region Combined Authority"},
        )

        authority = authorities.get("LIV")

        assert (
            authority
            and authority.abbreviation == "LIV"
            and authority.name == "Liverpool City Region Combined Authority"
        )
