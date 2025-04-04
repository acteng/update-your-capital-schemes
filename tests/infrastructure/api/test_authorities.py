import pytest
import responses
from authlib.integrations.flask_client import FlaskIntegration, FlaskOAuth2App
from responses.matchers import header_matcher

from schemes.infrastructure.api.authorities import ApiAuthorityRepository


class TestApiAuthorityRepository:
    @pytest.fixture(name="authorities")
    def authorities_fixture(self) -> ApiAuthorityRepository:
        remote_app = FlaskOAuth2App(
            FlaskIntegration("ate"), access_token_url="https://auth.example/token", api_base_url="https://api.example"
        )
        # TODO: extract out to oauth fixture?
        responses.post("https://auth.example/token", json={"access_token": "dummy_jwt"})
        return ApiAuthorityRepository(remote_app)

    @responses.activate
    def test_get_authority(self, authorities: ApiAuthorityRepository) -> None:
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
