from datetime import datetime, timezone
from typing import Any

import pytest
from pydantic import AnyUrl
from respx import MockRouter

from schemes.domain.schemes.funding import BidStatus
from schemes.domain.schemes.overview import FundingProgrammes
from schemes.infrastructure.api.funding_programmes import FundingProgrammeItemModel
from schemes.infrastructure.api.schemes import (
    ApiSchemeRepository,
    BidStatusModel,
    CapitalSchemeAuthorityReviewModel,
    CapitalSchemeBidStatusDetailsModel,
    CapitalSchemeModel,
    CapitalSchemeOverviewModel,
)
from schemes.oauth import ClientAsyncBaseApp
from tests.infrastructure.api.conftest import StubRemoteApp


class TestApiSchemeRepository:
    @pytest.fixture(name="schemes")
    def schemes_fixture(self, remote_app: ClientAsyncBaseApp) -> ApiSchemeRepository:
        return ApiSchemeRepository(remote_app)

    async def test_get_schemes_by_authority(
        self, api_mock: MockRouter, api_base_url: str, schemes: ApiSchemeRepository
    ) -> None:
        api_mock.get("/funding-programmes").respond(200, json={"items": [_dummy_funding_programme_item_json()]})
        api_mock.get("/capital-schemes/milestones").respond(200, json={"items": []})
        api_mock.get("/authorities/LIV/capital-schemes/bid-submitting").respond(
            200,
            json={"items": [f"{api_base_url}/capital-schemes/ATE00001", f"{api_base_url}/capital-schemes/ATE00002"]},
        )
        api_mock.get("/capital-schemes/ATE00001").respond(200, json=_build_capital_scheme_json("ATE00001"))
        api_mock.get("/capital-schemes/ATE00002").respond(200, json=_build_capital_scheme_json("ATE00002"))

        scheme1, scheme2 = await schemes.get_by_authority("LIV")

        assert scheme1.reference == "ATE00001"
        assert scheme2.reference == "ATE00002"

    async def test_get_schemes_by_authority_sets_overview_revision(
        self, api_mock: MockRouter, api_base_url: str, schemes: ApiSchemeRepository
    ) -> None:
        api_mock.get("/funding-programmes").respond(
            200, json={"items": [{"@id": f"{api_base_url}/funding-programmes/ATF4", "code": "ATF4"}]}
        )
        api_mock.get("/capital-schemes/milestones").respond(200, json={"items": []})
        api_mock.get("/authorities/LIV/capital-schemes/bid-submitting").respond(
            200, json={"items": [f"{api_base_url}/capital-schemes/ATE00001"]}
        )
        api_mock.get("/capital-schemes/ATE00001").respond(
            200,
            json={
                "reference": "ATE00001",
                "overview": {
                    "name": "Wirral Package",
                    "fundingProgramme": f"{api_base_url}/funding-programmes/ATF4",
                },
                "bidStatusDetails": _dummy_bid_status_details_json(),
            },
        )

        (scheme1,) = await schemes.get_by_authority("LIV")

        assert scheme1.reference == "ATE00001"
        (overview_revision1,) = scheme1.overview.overview_revisions
        assert (
            overview_revision1.name == "Wirral Package"
            and overview_revision1.funding_programme == FundingProgrammes.ATF4
        )

    async def test_get_schemes_by_authority_sets_bid_status_revision(
        self, api_mock: MockRouter, api_base_url: str, schemes: ApiSchemeRepository
    ) -> None:
        api_mock.get("/funding-programmes").respond(200, json={"items": [_dummy_funding_programme_item_json()]})
        api_mock.get("/capital-schemes/milestones").respond(200, json={"items": []})
        api_mock.get("/authorities/LIV/capital-schemes/bid-submitting").respond(
            200, json={"items": [f"{api_base_url}/capital-schemes/ATE00001"]}
        )
        api_mock.get("/capital-schemes/ATE00001").respond(
            200,
            json={
                "reference": "ATE00001",
                "overview": _dummy_overview_json(),
                "bidStatusDetails": {"bidStatus": "funded"},
            },
        )

        (scheme1,) = await schemes.get_by_authority("LIV")

        assert scheme1.reference == "ATE00001"
        (bid_status_revision1,) = scheme1.funding.bid_status_revisions
        assert bid_status_revision1.status == BidStatus.FUNDED

    async def test_get_schemes_by_authority_sets_authority_review(
        self, api_mock: MockRouter, api_base_url: str, schemes: ApiSchemeRepository
    ) -> None:
        api_mock.get("/funding-programmes").respond(200, json={"items": [_dummy_funding_programme_item_json()]})
        api_mock.get("/capital-schemes/milestones").respond(200, json={"items": []})
        api_mock.get("/authorities/LIV/capital-schemes/bid-submitting").respond(
            200, json={"items": [f"{api_base_url}/capital-schemes/ATE00001"]}
        )
        api_mock.get("/capital-schemes/ATE00001").respond(
            200,
            json={
                "reference": "ATE00001",
                "overview": _dummy_overview_json(),
                "bidStatusDetails": _dummy_bid_status_details_json(),
                "authorityReview": {"reviewDate": "2020-01-02T00:00:00Z"},
            },
        )

        (scheme1,) = await schemes.get_by_authority("LIV")

        assert scheme1.reference == "ATE00001"
        (authority_review1,) = scheme1.reviews.authority_reviews
        assert authority_review1.review_date == datetime(2020, 1, 2)

    async def test_get_schemes_by_authority_filters_by_funding_programme_eligible_for_authority_update(
        self, api_mock: MockRouter, api_base_url: str, schemes: ApiSchemeRepository
    ) -> None:
        api_mock.get("/funding-programmes", params={"eligible-for-authority-update": "true"}).respond(
            200,
            json={
                "items": [
                    {"@id": f"{api_base_url}/funding-programmes/ATF3", "code": "ATF3"},
                    {"@id": f"{api_base_url}/funding-programmes/ATF4", "code": "ATF4"},
                ]
            },
        )
        api_mock.get("/capital-schemes/milestones").respond(200, json={"items": []})
        api_mock.get(
            "/authorities/LIV/capital-schemes/bid-submitting", params={"funding-programme-code": ["ATF3", "ATF4"]}
        ).respond(200, json={"items": [f"{api_base_url}/capital-schemes/ATE00001"]})
        api_mock.get("/capital-schemes/ATE00001").respond(
            200,
            json={
                "reference": "ATE00001",
                "overview": {
                    "name": "Wirral Package",
                    "fundingProgramme": f"{api_base_url}/funding-programmes/ATF4",
                },
                "bidStatusDetails": _dummy_bid_status_details_json(),
            },
        )

        (scheme1,) = await schemes.get_by_authority("LIV")

        assert scheme1.reference == "ATE00001"

    async def test_get_schemes_by_authority_filters_by_bid_status_funded(
        self, api_mock: MockRouter, api_base_url: str, schemes: ApiSchemeRepository
    ) -> None:
        api_mock.get("/funding-programmes").respond(200, json={"items": [_dummy_funding_programme_item_json()]})
        api_mock.get("/capital-schemes/milestones").respond(200, json={"items": []})
        api_mock.get("/authorities/LIV/capital-schemes/bid-submitting", params={"bid-status": "funded"}).respond(
            200, json={"items": [f"{api_base_url}/capital-schemes/ATE00001"]}
        )
        api_mock.get("/capital-schemes/ATE00001").respond(200, json=_build_capital_scheme_json("ATE00001"))

        (scheme1,) = await schemes.get_by_authority("LIV")

        assert scheme1.reference == "ATE00001"

    async def test_get_schemes_by_authority_filters_by_current_milestone_active_and_incomplete(
        self, api_mock: MockRouter, api_base_url: str, schemes: ApiSchemeRepository
    ) -> None:
        api_mock.get("/funding-programmes").respond(200, json={"items": [_dummy_funding_programme_item_json()]})
        api_mock.get("/capital-schemes/milestones", params={"active": "true", "complete": "false"}).respond(
            200, json={"items": ["detailed design completed", "construction started"]}
        )
        api_mock.get(
            "/authorities/LIV/capital-schemes/bid-submitting",
            params={"current-milestone": ["detailed design completed", "construction started", ""]},
        ).respond(200, json={"items": [f"{api_base_url}/capital-schemes/ATE00001"]})
        api_mock.get("/capital-schemes/ATE00001").respond(200, json=_build_capital_scheme_json("ATE00001"))

        (scheme1,) = await schemes.get_by_authority("LIV")

        assert scheme1.reference == "ATE00001"

    async def test_get_schemes_by_authority_reuses_client(
        self, api_mock: MockRouter, api_base_url: str, remote_app: StubRemoteApp, schemes: ApiSchemeRepository
    ) -> None:
        api_mock.get("/funding-programmes").respond(200, json={"items": [_dummy_funding_programme_item_json()]})
        api_mock.get("/capital-schemes/milestones").respond(200, json={"items": []})
        api_mock.get("/authorities/LIV/capital-schemes/bid-submitting").respond(
            200,
            json={"items": [f"{api_base_url}/capital-schemes/ATE00001", f"{api_base_url}/capital-schemes/ATE00002"]},
        )
        api_mock.get("/capital-schemes/ATE00001").respond(200, json=_build_capital_scheme_json("ATE00001"))
        api_mock.get("/capital-schemes/ATE00002").respond(200, json=_build_capital_scheme_json("ATE00002"))

        await schemes.get_by_authority("LIV")

        assert remote_app.client_count == 1


class TestCapitalSchemeOverviewModel:
    def test_to_domain(self) -> None:
        funding_programme_item_model = FundingProgrammeItemModel(
            id=AnyUrl("https://api.example/funding-programmes/ATF4"), code="ATF4"
        )
        overview_model = CapitalSchemeOverviewModel(
            name="Wirral Package", funding_programme=AnyUrl("https://api.example/funding-programmes/ATF4")
        )

        overview_revision = overview_model.to_domain([funding_programme_item_model])

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
        funding_programme_item_model = FundingProgrammeItemModel(
            id=AnyUrl("https://api.example/funding-programmes/ATF4"), code="ATF4"
        )
        capital_scheme_model = CapitalSchemeModel(
            reference="ATE00001",
            overview=CapitalSchemeOverviewModel(
                name="Wirral Package", funding_programme=AnyUrl("https://api.example/funding-programmes/ATF4")
            ),
            bid_status_details=_dummy_bid_status_details_model(),
        )

        scheme = capital_scheme_model.to_domain([funding_programme_item_model])

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

        scheme = capital_scheme_model.to_domain([_dummy_funding_programme_item_model()])

        assert scheme.reference == "ATE00001"
        (authority_review1,) = scheme.reviews.authority_reviews
        assert authority_review1.review_date == datetime(2020, 1, 2)


def _dummy_funding_programme_item_json() -> dict[str, Any]:
    return {"@id": "https://api.example/funding-programmes/dummy", "code": "dummy"}


def _dummy_overview_json() -> dict[str, Any]:
    return {"name": "", "fundingProgramme": "https://api.example/funding-programmes/dummy"}


def _dummy_bid_status_details_json() -> dict[str, Any]:
    return {"bidStatus": "submitted"}


def _build_capital_scheme_json(reference: str) -> dict[str, Any]:
    return {
        "reference": reference,
        "overview": _dummy_overview_json(),
        "bidStatusDetails": _dummy_bid_status_details_json(),
    }


def _dummy_funding_programme_item_model() -> FundingProgrammeItemModel:
    return FundingProgrammeItemModel(id=AnyUrl("https://api.example/funding-programmes/dummy"), code="dummy")


def _dummy_overview_model() -> CapitalSchemeOverviewModel:
    return CapitalSchemeOverviewModel(name="", funding_programme=_dummy_funding_programme_item_model().id)


def _dummy_bid_status_details_model() -> CapitalSchemeBidStatusDetailsModel:
    return CapitalSchemeBidStatusDetailsModel(bid_status=BidStatusModel.SUBMITTED)
