import pytest
from pydantic import AnyUrl
from respx import MockRouter

from schemes.infrastructure.api.authorities import ApiAuthorityRepository, AuthorityModel
from schemes.oauth import AsyncBaseApp
from tests.unit.infrastructure.api.builders import build_authority_json


class TestAuthorityModel:
    def test_to_domain(self) -> None:
        authority_model = AuthorityModel(
            id=AnyUrl("https://api.example/authorities/LIV"),
            abbreviation="LIV",
            full_name="Liverpool City Region Combined Authority",
            bid_submitting_capital_schemes=AnyUrl("https://api.example/authorities/LIV/capital-schemes/bid-submitting"),
        )

        authority = authority_model.to_domain()

        assert authority.abbreviation == "LIV" and authority.name == "Liverpool City Region Combined Authority"


class TestApiAuthorityRepository:
    @pytest.fixture(name="authorities")
    def authorities_fixture(self, remote_app: AsyncBaseApp) -> ApiAuthorityRepository:
        return ApiAuthorityRepository(remote_app)

    async def test_get_authority(self, api_mock: MockRouter, authorities: ApiAuthorityRepository) -> None:
        api_mock.get("/authorities/LIV").respond(
            json=build_authority_json(abbreviation="LIV", full_name="Liverpool City Region Combined Authority")
        )

        authority = await authorities.get("LIV")

        assert (
            authority
            and authority.abbreviation == "LIV"
            and authority.name == "Liverpool City Region Combined Authority"
        )

    async def test_get_authority_ignores_unknown_key(
        self, api_mock: MockRouter, authorities: ApiAuthorityRepository
    ) -> None:
        api_mock.get("/authorities/LIV").respond(
            json=build_authority_json(abbreviation="LIV", full_name="Liverpool City Region Combined Authority")
            | {"foo": "bar"},
        )

        authority = await authorities.get("LIV")

        assert (
            authority
            and authority.abbreviation == "LIV"
            and authority.name == "Liverpool City Region Combined Authority"
        )

    async def test_get_authority_that_does_not_exist(
        self, api_mock: MockRouter, authorities: ApiAuthorityRepository
    ) -> None:
        api_mock.get("/authorities/WYO").respond(404)

        assert await authorities.get("WYO") is None
