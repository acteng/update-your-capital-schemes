import pytest
import responses
from responses.matchers import header_matcher

from schemes.infrastructure.api.authorities import ApiAuthorityRepository, RemoteApp
from tests.infrastructure.api.oauth import StubAuthorizationServer


class TestApiAuthorityRepository:
    @pytest.fixture(name="authorities")
    def authorities_fixture(self, remote_app: RemoteApp) -> ApiAuthorityRepository:
        return ApiAuthorityRepository(remote_app)

    @responses.activate
    def test_get_authority(
        self, authorization_server: StubAuthorizationServer, api_base_url: str, authorities: ApiAuthorityRepository
    ) -> None:
        authorization_server.given_token_endpoint_returns_access_token("dummy_jwt")
        responses.get(
            f"{api_base_url}/authorities/LIV",
            match=[header_matcher({"Authorization": "Bearer dummy_jwt"})],
            json={"abbreviation": "LIV", "fullName": "Liverpool City Region Combined Authority"},
        )

        authority = authorities.get("LIV")

        assert (
            authority
            and authority.abbreviation == "LIV"
            and authority.name == "Liverpool City Region Combined Authority"
        )
