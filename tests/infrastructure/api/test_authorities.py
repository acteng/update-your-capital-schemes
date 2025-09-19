import pytest
import respx

from schemes.infrastructure.api.authorities import ApiAuthorityRepository, AuthorityModel
from schemes.oauth import AsyncBaseApp


class TestApiAuthorityRepository:
    @pytest.fixture(name="authorities")
    def authorities_fixture(self, remote_app: AsyncBaseApp) -> ApiAuthorityRepository:
        return ApiAuthorityRepository(remote_app)

    @respx.mock
    async def test_get_authority(
        self, access_token: str, api_base_url: str, authorities: ApiAuthorityRepository
    ) -> None:
        respx.get(f"{api_base_url}/authorities/LIV", headers={"Authorization": f"Bearer {access_token}"}).respond(
            200, json={"abbreviation": "LIV", "fullName": "Liverpool City Region Combined Authority"}
        )

        authority = await authorities.get("LIV")

        assert (
            authority
            and authority.abbreviation == "LIV"
            and authority.name == "Liverpool City Region Combined Authority"
        )

    @respx.mock
    async def test_get_authority_ignores_unknown_key(
        self, access_token: str, api_base_url: str, authorities: ApiAuthorityRepository
    ) -> None:
        respx.get(f"{api_base_url}/authorities/LIV", headers={"Authorization": f"Bearer {access_token}"}).respond(
            200, json={"abbreviation": "LIV", "fullName": "Liverpool City Region Combined Authority", "foo": "bar"}
        )

        authority = await authorities.get("LIV")

        assert (
            authority
            and authority.abbreviation == "LIV"
            and authority.name == "Liverpool City Region Combined Authority"
        )

    @respx.mock
    async def test_get_authority_that_does_not_exist(
        self, access_token: str, api_base_url: str, authorities: ApiAuthorityRepository
    ) -> None:
        respx.get(f"{api_base_url}/authorities/WYO", headers={"Authorization": f"Bearer {access_token}"}).respond(404)

        assert await authorities.get("WYO") is None


class TestAuthorityModel:
    def test_to_domain(self) -> None:
        authority_model = AuthorityModel(abbreviation="LIV", full_name="Liverpool City Region Combined Authority")

        authority = authority_model.to_domain()

        assert authority.abbreviation == "LIV" and authority.name == "Liverpool City Region Combined Authority"
