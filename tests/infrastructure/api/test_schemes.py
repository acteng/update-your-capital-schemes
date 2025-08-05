from datetime import datetime, timezone
from typing import Any

import pytest
import responses
from responses.matchers import header_matcher

from schemes.infrastructure.api.oauth import RemoteApp
from schemes.infrastructure.api.schemes import (
    ApiSchemeRepository,
    CapitalSchemeAuthorityReviewModel,
    CapitalSchemeModel,
    CapitalSchemeOverviewModel,
)


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
            json={"reference": "ATE00001", "overview": _dummy_overview_json()},
        )
        responses.get(
            f"{api_base_url}/capital-schemes/ATE00002",
            match=[header_matcher({"Authorization": f"Bearer {access_token}"})],
            json={"reference": "ATE00002", "overview": _dummy_overview_json()},
        )

        scheme1, scheme2 = schemes.get_by_authority("LIV")

        assert scheme1.reference == "ATE00001"
        assert scheme2.reference == "ATE00002"

    @responses.activate
    def test_get_by_authority_sets_overview_revision(
        self, access_token: str, api_base_url: str, schemes: ApiSchemeRepository
    ) -> None:
        responses.get(
            f"{api_base_url}/authorities/LIV/capital-schemes/bid-submitting",
            match=[header_matcher({"Authorization": f"Bearer {access_token}"})],
            json={"items": [f"{api_base_url}/capital-schemes/ATE00001"]},
        )
        responses.get(
            f"{api_base_url}/capital-schemes/ATE00001",
            match=[header_matcher({"Authorization": f"Bearer {access_token}"})],
            json={"reference": "ATE00001", "overview": {"name": "Wirral Package"}},
        )

        (scheme1,) = schemes.get_by_authority("LIV")

        assert scheme1.reference == "ATE00001"
        (overview_revision1,) = scheme1.overview.overview_revisions
        assert overview_revision1.name == "Wirral Package"

    @responses.activate
    def test_get_by_authority_sets_authority_review(
        self, access_token: str, api_base_url: str, schemes: ApiSchemeRepository
    ) -> None:
        responses.get(
            f"{api_base_url}/authorities/LIV/capital-schemes/bid-submitting",
            match=[header_matcher({"Authorization": f"Bearer {access_token}"})],
            json={"items": [f"{api_base_url}/capital-schemes/ATE00001"]},
        )
        responses.get(
            f"{api_base_url}/capital-schemes/ATE00001",
            match=[header_matcher({"Authorization": f"Bearer {access_token}"})],
            json={
                "reference": "ATE00001",
                "overview": _dummy_overview_json(),
                "authorityReview": {"reviewDate": "2020-01-02T00:00:00Z"},
            },
        )

        (scheme1,) = schemes.get_by_authority("LIV")

        assert scheme1.reference == "ATE00001"
        (authority_review1,) = scheme1.reviews.authority_reviews
        assert authority_review1.review_date == datetime(2020, 1, 2)


class TestCapitalSchemeOverviewModel:
    def test_to_domain(self) -> None:
        overview_model = CapitalSchemeOverviewModel(name="Wirral Package")

        overview_revision = overview_model.to_domain()

        assert overview_revision.name == "Wirral Package"


class TestCapitalSchemeAuthorityReviewModel:
    def test_to_domain(self) -> None:
        authority_review_model = CapitalSchemeAuthorityReviewModel(review_date=datetime(2020, 1, 2))

        authority_review = authority_review_model.to_domain()

        assert authority_review.review_date == datetime(2020, 1, 2)

    def test_to_domain_converts_dates_to_local_europe_london(self) -> None:
        authority_review_model = CapitalSchemeAuthorityReviewModel(
            review_date=datetime(2020, 6, 1, 12, tzinfo=timezone.utc)
        )

        authority_review = authority_review_model.to_domain()

        assert authority_review.review_date == datetime(2020, 6, 1, 13)


class TestCapitalSchemeModel:
    def test_to_domain(self) -> None:
        capital_scheme_model = CapitalSchemeModel(
            reference="ATE00001", overview=CapitalSchemeOverviewModel(name="Wirral Package")
        )

        scheme = capital_scheme_model.to_domain()

        assert scheme.reference == "ATE00001"
        (overview_revision1,) = scheme.overview.overview_revisions
        assert overview_revision1.name == "Wirral Package"
        assert not scheme.reviews.authority_reviews

    def test_to_domain_sets_authority_review(self) -> None:
        capital_scheme_model = CapitalSchemeModel(
            reference="ATE00001",
            overview=_dummy_overview_model(),
            authority_review=CapitalSchemeAuthorityReviewModel(review_date=datetime(2020, 1, 2)),
        )

        scheme = capital_scheme_model.to_domain()

        assert scheme.reference == "ATE00001"
        (authority_review1,) = scheme.reviews.authority_reviews
        assert authority_review1.review_date == datetime(2020, 1, 2)


def _dummy_overview_model() -> CapitalSchemeOverviewModel:
    return CapitalSchemeOverviewModel(name="")


def _dummy_overview_json() -> dict[str, Any]:
    return {"name": ""}
