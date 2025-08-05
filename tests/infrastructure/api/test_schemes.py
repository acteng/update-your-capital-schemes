import pytest
import responses
from responses.matchers import header_matcher

from schemes.infrastructure.api.oauth import RemoteApp
from schemes.infrastructure.api.schemes import ApiSchemeRepository, CapitalSchemeModel


class TestApiSchemeRepository:
    @pytest.fixture(name="schemes")
    def schemes_fixture(self, remote_app: RemoteApp) -> ApiSchemeRepository:
        return ApiSchemeRepository(remote_app)

    @responses.activate
    def test_get_by_authority(self, access_token: str, api_base_url: str, schemes: ApiSchemeRepository) -> None:
        responses.get(
            f"{api_base_url}/authorities/LIV/capital-schemes/bid-submitting",
            match=[header_matcher({"Authorization": f"Bearer {access_token}"})],
            json={
                "items": [
                    f"{api_base_url}/capital-schemes/ATE00001",
                    f"{api_base_url}/capital-schemes/ATE00002",
                ]
            },
        )
        responses.get(
            f"{api_base_url}/capital-schemes/ATE00001",
            match=[header_matcher({"Authorization": f"Bearer {access_token}"})],
            json={"reference": "ATE00001"},
        )
        responses.get(
            f"{api_base_url}/capital-schemes/ATE00002",
            match=[header_matcher({"Authorization": f"Bearer {access_token}"})],
            json={"reference": "ATE00002"},
        )

        scheme1, scheme2 = schemes.get_by_authority("LIV")

        assert scheme1.reference == "ATE00001"
        assert scheme2.reference == "ATE00002"


class TestCapitalSchemeModel:
    def test_to_domain(self) -> None:
        capital_scheme_model = CapitalSchemeModel(reference="ATE00001")

        scheme = capital_scheme_model.to_domain()

        assert scheme.reference == "ATE00001"
