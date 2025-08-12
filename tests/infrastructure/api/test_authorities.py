import pytest
from responses import RequestsMock
from responses.matchers import header_matcher

from schemes.infrastructure.api.authorities import ApiAuthorityRepository, AuthorityModel
from schemes.infrastructure.api.oauth import RemoteApp


class TestApiAuthorityRepository:
    @pytest.fixture(name="authorities")
    def authorities_fixture(self, remote_app: RemoteApp) -> ApiAuthorityRepository:
        return ApiAuthorityRepository(remote_app)

    def test_get_authority(
        self, responses: RequestsMock, access_token: str, api_base_url: str, authorities: ApiAuthorityRepository
    ) -> None:
        responses.get(
            f"{api_base_url}/authorities/LIV",
            match=[header_matcher({"Authorization": f"Bearer {access_token}"})],
            json={"abbreviation": "LIV", "fullName": "Liverpool City Region Combined Authority"},
        )

        authority = authorities.get("LIV")

        assert (
            authority
            and authority.abbreviation == "LIV"
            and authority.name == "Liverpool City Region Combined Authority"
        )

    def test_get_authority_ignores_unknown_key(
        self, responses: RequestsMock, access_token: str, api_base_url: str, authorities: ApiAuthorityRepository
    ) -> None:
        responses.get(
            f"{api_base_url}/authorities/LIV",
            match=[header_matcher({"Authorization": f"Bearer {access_token}"})],
            json={"abbreviation": "LIV", "fullName": "Liverpool City Region Combined Authority", "foo": "bar"},
        )

        authority = authorities.get("LIV")

        assert (
            authority
            and authority.abbreviation == "LIV"
            and authority.name == "Liverpool City Region Combined Authority"
        )

    def test_get_authority_that_does_not_exist(
        self, responses: RequestsMock, access_token: str, api_base_url: str, authorities: ApiAuthorityRepository
    ) -> None:
        responses.get(
            f"{api_base_url}/authorities/WYO",
            match=[header_matcher({"Authorization": f"Bearer {access_token}"})],
            status=404,
        )

        assert authorities.get("WYO") is None


class TestAuthorityModel:
    def test_to_domain(self) -> None:
        authority_model = AuthorityModel(abbreviation="LIV", full_name="Liverpool City Region Combined Authority")

        authority = authority_model.to_domain()

        assert authority.abbreviation == "LIV" and authority.name == "Liverpool City Region Combined Authority"
