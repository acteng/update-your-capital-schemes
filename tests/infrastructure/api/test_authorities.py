from typing import Any

import pytest
from pydantic import AnyUrl
from respx import MockRouter

from schemes.infrastructure.api.authorities import ApiAuthorityRepository, AuthorityModel
from schemes.oauth import AsyncBaseApp


class TestApiAuthorityRepository:
    @pytest.fixture(name="authorities")
    def authorities_fixture(self, remote_app: AsyncBaseApp) -> ApiAuthorityRepository:
        return ApiAuthorityRepository(remote_app)

    async def test_get_authority(self, api_mock: MockRouter, authorities: ApiAuthorityRepository) -> None:
        api_mock.get("/authorities/LIV").respond(
            200, json=_build_authority_json(abbreviation="LIV", full_name="Liverpool City Region Combined Authority")
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
            200,
            json=_build_authority_json(abbreviation="LIV", full_name="Liverpool City Region Combined Authority")
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


class TestAuthorityModel:
    def test_to_domain(self) -> None:
        authority_model = AuthorityModel(
            id=AnyUrl("https://api.example/authorities/LIV"),
            abbreviation="LIV",
            full_name="Liverpool City Region Combined Authority",
        )

        authority = authority_model.to_domain()

        assert authority.abbreviation == "LIV" and authority.name == "Liverpool City Region Combined Authority"


def _build_authority_json(
    id_: str | None = None, abbreviation: str | None = None, full_name: str | None = None
) -> dict[str, Any]:
    return {
        "@id": id_ or "https://api.example/authorities/dummy",
        "abbreviation": abbreviation or "dummy",
        "fullName": full_name or "dummy",
    }
