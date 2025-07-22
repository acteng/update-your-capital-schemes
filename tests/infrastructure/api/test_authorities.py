import pytest
import responses
from responses.matchers import header_matcher

from schemes.infrastructure.api import ApiAuthorityRepository, RemoteApp
from schemes.infrastructure.api.authorities import AuthorityRepr


class TestApiAuthorityRepository:
    @pytest.fixture(name="authorities")
    def authorities_fixture(self, remote_app: RemoteApp) -> ApiAuthorityRepository:
        return ApiAuthorityRepository(remote_app)

    @responses.activate
    def test_get_authority(self, access_token: str, api_base_url: str, authorities: ApiAuthorityRepository) -> None:
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

    @responses.activate
    def test_get_authority_ignores_unknown_key(
        self, access_token: str, api_base_url: str, authorities: ApiAuthorityRepository
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

    @responses.activate
    def test_get_authority_that_does_not_exist(
        self, access_token: str, api_base_url: str, authorities: ApiAuthorityRepository
    ) -> None:
        responses.get(
            f"{api_base_url}/authorities/WYO",
            match=[header_matcher({"Authorization": f"Bearer {access_token}"})],
            status=404,
        )

        assert authorities.get("WYO") is None


class TestAuthorityRepr:
    def test_to_domain(self) -> None:
        authority_repr = AuthorityRepr(abbreviation="LIV", full_name="Liverpool City Region Combined Authority")

        authority = authority_repr.to_domain()

        assert authority.abbreviation == "LIV" and authority.name == "Liverpool City Region Combined Authority"
