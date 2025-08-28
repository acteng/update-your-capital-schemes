from datetime import datetime, timezone
from typing import Any

import pytest
from authlib.integrations.base_client import BaseApp
from pydantic import AnyUrl
from responses import RequestsMock
from responses.matchers import header_matcher, query_param_matcher

from schemes.domain.schemes.funding import BidStatus
from schemes.domain.schemes.overview import FundingProgramme, FundingProgrammes
from schemes.infrastructure.api.schemes import (
    ApiSchemeRepository,
    BidStatusModel,
    CapitalSchemeAuthorityReviewModel,
    CapitalSchemeBidStatusDetailsModel,
    CapitalSchemeModel,
    CapitalSchemeOverviewModel,
    FundingProgrammeItemModel,
)


class TestApiSchemeRepository:
    @pytest.fixture(name="schemes")
    def schemes_fixture(self, remote_app: BaseApp) -> ApiSchemeRepository:
        return ApiSchemeRepository(remote_app)

    def test_get_by_authority(
        self, responses: RequestsMock, access_token: str, api_base_url: str, schemes: ApiSchemeRepository
    ) -> None:
        responses.get(
            f"{api_base_url}/funding-programmes",
            match=[header_matcher({"Authorization": f"Bearer {access_token}"})],
            json=_dummy_funding_programmes_json(),
        )
        responses.get(
            f"{api_base_url}/capital-schemes/milestones",
            match=[header_matcher({"Authorization": f"Bearer {access_token}"})],
            json=_dummy_milestones_json(),
        )
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
            json=_build_capital_scheme_json("ATE00001"),
        )
        responses.get(
            f"{api_base_url}/capital-schemes/ATE00002",
            match=[header_matcher({"Authorization": f"Bearer {access_token}"})],
            json=_build_capital_scheme_json("ATE00002"),
        )

        scheme1, scheme2 = schemes.get_by_authority("LIV")

        assert scheme1.reference == "ATE00001"
        assert scheme2.reference == "ATE00002"

    def test_get_by_authority_sets_overview_revision(
        self, responses: RequestsMock, access_token: str, api_base_url: str, schemes: ApiSchemeRepository
    ) -> None:
        responses.get(
            f"{api_base_url}/funding-programmes",
            match=[header_matcher({"Authorization": f"Bearer {access_token}"})],
            json={"items": [{"@id": f"{api_base_url}/funding-programmes/ATF4", "code": "ATF4"}]},
        )
        responses.get(
            f"{api_base_url}/capital-schemes/milestones",
            match=[header_matcher({"Authorization": f"Bearer {access_token}"})],
            json=_dummy_milestones_json(),
        )
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
                "overview": {"name": "Wirral Package", "fundingProgramme": f"{api_base_url}/funding-programmes/ATF4"},
                "bidStatusDetails": _dummy_bid_status_details_json(),
            },
        )

        (scheme1,) = schemes.get_by_authority("LIV")

        assert scheme1.reference == "ATE00001"
        (overview_revision1,) = scheme1.overview.overview_revisions
        assert (
            overview_revision1.name == "Wirral Package"
            and overview_revision1.funding_programme == FundingProgrammes.ATF4
        )

    def test_get_by_authority_sets_bid_status_revision(
        self, responses: RequestsMock, access_token: str, api_base_url: str, schemes: ApiSchemeRepository
    ) -> None:
        responses.get(
            f"{api_base_url}/funding-programmes",
            match=[header_matcher({"Authorization": f"Bearer {access_token}"})],
            json=_dummy_funding_programmes_json(),
        )
        responses.get(
            f"{api_base_url}/capital-schemes/milestones",
            match=[header_matcher({"Authorization": f"Bearer {access_token}"})],
            json=_dummy_milestones_json(),
        )
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
                "bidStatusDetails": {"bidStatus": "funded"},
            },
        )

        (scheme1,) = schemes.get_by_authority("LIV")

        assert scheme1.reference == "ATE00001"
        (bid_status_revision1,) = scheme1.funding.bid_status_revisions
        assert bid_status_revision1.status == BidStatus.FUNDED

    def test_get_by_authority_sets_authority_review(
        self, responses: RequestsMock, access_token: str, api_base_url: str, schemes: ApiSchemeRepository
    ) -> None:
        responses.get(
            f"{api_base_url}/funding-programmes",
            match=[header_matcher({"Authorization": f"Bearer {access_token}"})],
            json=_dummy_funding_programmes_json(),
        )
        responses.get(
            f"{api_base_url}/capital-schemes/milestones",
            match=[header_matcher({"Authorization": f"Bearer {access_token}"})],
            json=_dummy_milestones_json(),
        )
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
                "bidStatusDetails": _dummy_bid_status_details_json(),
                "authorityReview": {"reviewDate": "2020-01-02T00:00:00Z"},
            },
        )

        (scheme1,) = schemes.get_by_authority("LIV")

        assert scheme1.reference == "ATE00001"
        (authority_review1,) = scheme1.reviews.authority_reviews
        assert authority_review1.review_date == datetime(2020, 1, 2)

    def test_get_by_authority_filters_by_funding_programme_eligible_for_authority_update(
        self, responses: RequestsMock, access_token: str, api_base_url: str, schemes: ApiSchemeRepository
    ) -> None:
        responses.get(
            f"{api_base_url}/funding-programmes",
            match=[
                query_param_matcher({"eligible-for-authority-update": "true"}),
                header_matcher({"Authorization": f"Bearer {access_token}"}),
            ],
            json={
                "items": [
                    {"@id": f"{api_base_url}/funding-programmes/ATF3", "code": "ATF3"},
                    {"@id": f"{api_base_url}/funding-programmes/ATF4", "code": "ATF4"},
                ]
            },
        )
        responses.get(
            f"{api_base_url}/capital-schemes/milestones",
            match=[header_matcher({"Authorization": f"Bearer {access_token}"})],
            json=_dummy_milestones_json(),
        )
        responses.get(
            f"{api_base_url}/authorities/LIV/capital-schemes/bid-submitting",
            match=[
                query_param_matcher({"funding-programme-code": ["ATF3", "ATF4"]}, strict_match=False),
                header_matcher({"Authorization": f"Bearer {access_token}"}),
            ],
            json={"items": [f"{api_base_url}/capital-schemes/ATE00001"]},
        )
        responses.get(
            f"{api_base_url}/capital-schemes/ATE00001",
            match=[header_matcher({"Authorization": f"Bearer {access_token}"})],
            json={
                "reference": "ATE00001",
                "overview": {"name": "Wirral Package", "fundingProgramme": f"{api_base_url}/funding-programmes/ATF4"},
                "bidStatusDetails": _dummy_bid_status_details_json(),
            },
        )

        (scheme1,) = schemes.get_by_authority("LIV")

        assert scheme1.reference == "ATE00001"

    def test_get_by_authority_filters_by_bid_status_funded(
        self, responses: RequestsMock, access_token: str, api_base_url: str, schemes: ApiSchemeRepository
    ) -> None:
        responses.get(
            f"{api_base_url}/funding-programmes",
            match=[header_matcher({"Authorization": f"Bearer {access_token}"})],
            json=_dummy_funding_programmes_json(),
        )
        responses.get(
            f"{api_base_url}/capital-schemes/milestones",
            match=[header_matcher({"Authorization": f"Bearer {access_token}"})],
            json=_dummy_milestones_json(),
        )
        responses.get(
            f"{api_base_url}/authorities/LIV/capital-schemes/bid-submitting",
            match=[
                query_param_matcher({"bid-status": "funded"}, strict_match=False),
                header_matcher({"Authorization": f"Bearer {access_token}"}),
            ],
            json={"items": [f"{api_base_url}/capital-schemes/ATE00001"]},
        )
        responses.get(
            f"{api_base_url}/capital-schemes/ATE00001",
            match=[header_matcher({"Authorization": f"Bearer {access_token}"})],
            json=_build_capital_scheme_json("ATE00001"),
        )

        (scheme1,) = schemes.get_by_authority("LIV")

        assert scheme1.reference == "ATE00001"

    def test_get_by_authority_filters_by_current_milestone_active_and_incomplete(
        self, responses: RequestsMock, access_token: str, api_base_url: str, schemes: ApiSchemeRepository
    ) -> None:
        responses.get(
            f"{api_base_url}/funding-programmes",
            match=[header_matcher({"Authorization": f"Bearer {access_token}"})],
            json=_dummy_funding_programmes_json(),
        )
        responses.get(
            f"{api_base_url}/capital-schemes/milestones",
            match=[
                query_param_matcher({"active": "true", "complete": "false"}),
                header_matcher({"Authorization": f"Bearer {access_token}"}),
            ],
            json={"items": ["detailed design completed", "construction started"]},
        )
        responses.get(
            f"{api_base_url}/authorities/LIV/capital-schemes/bid-submitting",
            match=[
                query_param_matcher(
                    {"current-milestone": ["detailed design completed", "construction started", ""]}, strict_match=False
                ),
                header_matcher({"Authorization": f"Bearer {access_token}"}),
            ],
            json={"items": [f"{api_base_url}/capital-schemes/ATE00001"]},
        )
        responses.get(
            f"{api_base_url}/capital-schemes/ATE00001",
            match=[header_matcher({"Authorization": f"Bearer {access_token}"})],
            json=_build_capital_scheme_json("ATE00001"),
        )

        (scheme1,) = schemes.get_by_authority("LIV")

        assert scheme1.reference == "ATE00001"


class TestFundingProgrammeItemModel:
    def test_to_domain(self) -> None:
        funding_programme_item_model = FundingProgrammeItemModel(
            id=AnyUrl("https://api.example/funding-programmes/ATF4"), code="ATF4"
        )

        funding_programme = funding_programme_item_model.to_domain()

        assert funding_programme == FundingProgrammes.ATF4


class TestCapitalSchemeOverviewModel:
    def test_to_domain(self) -> None:
        funding_programmes = {"https://api.example/funding-programmes/ATF4": FundingProgrammes.ATF4}
        overview_model = CapitalSchemeOverviewModel(
            name="Wirral Package", funding_programme=AnyUrl("https://api.example/funding-programmes/ATF4")
        )

        overview_revision = overview_model.to_domain(funding_programmes)

        assert (
            overview_revision.name == "Wirral Package" and overview_revision.funding_programme == FundingProgrammes.ATF4
        )


class TestBidStatusModel:
    def test_to_domain(self) -> None:
        assert BidStatusModel.FUNDED.to_domain() == BidStatus.FUNDED


class TestCapitalSchemeBidStatusDetailsModel:
    def test_to_domain(self) -> None:
        bid_status_details_model = CapitalSchemeBidStatusDetailsModel(bid_status=BidStatusModel.FUNDED)

        bid_status_revision = bid_status_details_model.to_domain()

        assert bid_status_revision.status == BidStatus.FUNDED


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
        funding_programmes = {"https://api.example/funding-programmes/ATF4": FundingProgrammes.ATF4}
        capital_scheme_model = CapitalSchemeModel(
            reference="ATE00001",
            overview=CapitalSchemeOverviewModel(
                name="Wirral Package", funding_programme=AnyUrl("https://api.example/funding-programmes/ATF4")
            ),
            bid_status_details=_dummy_bid_status_details_model(),
        )

        scheme = capital_scheme_model.to_domain(funding_programmes)

        assert scheme.reference == "ATE00001"
        (overview_revision1,) = scheme.overview.overview_revisions
        assert (
            overview_revision1.name == "Wirral Package"
            and overview_revision1.funding_programme == FundingProgrammes.ATF4
        )
        assert not scheme.reviews.authority_reviews

    def test_to_domain_sets_authority_review(self) -> None:
        capital_scheme_model = CapitalSchemeModel(
            reference="ATE00001",
            overview=_dummy_overview_model(),
            bid_status_details=_dummy_bid_status_details_model(),
            authority_review=CapitalSchemeAuthorityReviewModel(review_date=datetime(2020, 1, 2)),
        )

        scheme = capital_scheme_model.to_domain(_dummy_funding_programmes())

        assert scheme.reference == "ATE00001"
        (authority_review1,) = scheme.reviews.authority_reviews
        assert authority_review1.review_date == datetime(2020, 1, 2)


def _dummy_funding_programme_url() -> str:
    return "https://api.example/funding-programmes/dummy"


def _dummy_funding_programme() -> FundingProgramme:
    return FundingProgramme(code="dummy", is_under_embargo=False, is_eligible_for_authority_update=True)


def _dummy_funding_programmes() -> dict[str, FundingProgramme]:
    return {_dummy_funding_programme_url(): _dummy_funding_programme()}


def _dummy_funding_programmes_json() -> dict[str, Any]:
    return {"items": [{"@id": _dummy_funding_programme_url(), "code": _dummy_funding_programme().code}]}


def _dummy_milestones_json() -> dict[str, Any]:
    return {"items": []}


def _dummy_overview_model() -> CapitalSchemeOverviewModel:
    return CapitalSchemeOverviewModel(name="", funding_programme=AnyUrl(_dummy_funding_programme_url()))


def _dummy_overview_json() -> dict[str, Any]:
    return {"name": "", "fundingProgramme": _dummy_funding_programme_url()}


def _dummy_bid_status_details_model() -> CapitalSchemeBidStatusDetailsModel:
    return CapitalSchemeBidStatusDetailsModel(bid_status=BidStatusModel.SUBMITTED)


def _dummy_bid_status_details_json() -> dict[str, Any]:
    return {"bidStatus": "submitted"}


def _build_capital_scheme_json(reference: str) -> dict[str, Any]:
    return {
        "reference": reference,
        "overview": _dummy_overview_json(),
        "bidStatusDetails": _dummy_bid_status_details_json(),
    }
