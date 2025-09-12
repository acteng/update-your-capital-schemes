from datetime import datetime, timezone
from typing import Any

import pytest
import respx
from httpx import Response
from pydantic import AnyUrl

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
from schemes.oauth import ClientAsyncBaseApp
from tests.infrastructure.api.conftest import StubRemoteApp


class TestApiSchemeRepository:
    @pytest.fixture(name="schemes")
    def schemes_fixture(self, remote_app: ClientAsyncBaseApp) -> ApiSchemeRepository:
        return ApiSchemeRepository(remote_app)

    @respx.mock
    async def test_get_by_authority(self, access_token: str, api_base_url: str, schemes: ApiSchemeRepository) -> None:
        respx.get(f"{api_base_url}/funding-programmes", headers={"Authorization": f"Bearer {access_token}"}).mock(
            return_value=Response(200, json=_dummy_funding_programmes_json())
        )
        respx.get(
            f"{api_base_url}/capital-schemes/milestones", headers={"Authorization": f"Bearer {access_token}"}
        ).mock(return_value=Response(200, json=_dummy_milestones_json()))
        respx.get(
            f"{api_base_url}/authorities/LIV/capital-schemes/bid-submitting",
            headers={"Authorization": f"Bearer {access_token}"},
        ).mock(
            return_value=Response(
                200,
                json={
                    "items": [
                        f"{api_base_url}/capital-schemes/ATE00001",
                        f"{api_base_url}/capital-schemes/ATE00002",
                    ]
                },
            )
        )
        respx.get(f"{api_base_url}/capital-schemes/ATE00001", headers={"Authorization": f"Bearer {access_token}"}).mock(
            return_value=Response(200, json=_build_capital_scheme_json("ATE00001"))
        )
        respx.get(f"{api_base_url}/capital-schemes/ATE00002", headers={"Authorization": f"Bearer {access_token}"}).mock(
            return_value=Response(200, json=_build_capital_scheme_json("ATE00002"))
        )

        scheme1, scheme2 = await schemes.get_by_authority("LIV")

        assert scheme1.reference == "ATE00001"
        assert scheme2.reference == "ATE00002"

    @respx.mock
    async def test_get_by_authority_sets_overview_revision(
        self, access_token: str, api_base_url: str, schemes: ApiSchemeRepository
    ) -> None:
        respx.get(f"{api_base_url}/funding-programmes", headers={"Authorization": f"Bearer {access_token}"}).mock(
            return_value=Response(
                200, json={"items": [{"@id": f"{api_base_url}/funding-programmes/ATF4", "code": "ATF4"}]}
            )
        )
        respx.get(
            f"{api_base_url}/capital-schemes/milestones", headers={"Authorization": f"Bearer {access_token}"}
        ).mock(return_value=Response(200, json=_dummy_milestones_json()))
        respx.get(
            f"{api_base_url}/authorities/LIV/capital-schemes/bid-submitting",
            headers={"Authorization": f"Bearer {access_token}"},
        ).mock(return_value=Response(200, json={"items": [f"{api_base_url}/capital-schemes/ATE00001"]}))
        respx.get(f"{api_base_url}/capital-schemes/ATE00001", headers={"Authorization": f"Bearer {access_token}"}).mock(
            return_value=Response(
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
        )

        (scheme1,) = await schemes.get_by_authority("LIV")

        assert scheme1.reference == "ATE00001"
        (overview_revision1,) = scheme1.overview.overview_revisions
        assert (
            overview_revision1.name == "Wirral Package"
            and overview_revision1.funding_programme == FundingProgrammes.ATF4
        )

    @respx.mock
    async def test_get_by_authority_sets_bid_status_revision(
        self, access_token: str, api_base_url: str, schemes: ApiSchemeRepository
    ) -> None:
        respx.get(f"{api_base_url}/funding-programmes", headers={"Authorization": f"Bearer {access_token}"}).mock(
            return_value=Response(200, json=_dummy_funding_programmes_json())
        )
        respx.get(
            f"{api_base_url}/capital-schemes/milestones", headers={"Authorization": f"Bearer {access_token}"}
        ).mock(return_value=Response(200, json=_dummy_milestones_json()))
        respx.get(
            f"{api_base_url}/authorities/LIV/capital-schemes/bid-submitting",
            headers={"Authorization": f"Bearer {access_token}"},
        ).mock(return_value=Response(200, json={"items": [f"{api_base_url}/capital-schemes/ATE00001"]}))
        respx.get(
            f"{api_base_url}/capital-schemes/ATE00001",
            headers={"Authorization": f"Bearer {access_token}"},
        ).mock(
            return_value=Response(
                200,
                json={
                    "reference": "ATE00001",
                    "overview": _dummy_overview_json(),
                    "bidStatusDetails": {"bidStatus": "funded"},
                },
            )
        )

        (scheme1,) = await schemes.get_by_authority("LIV")

        assert scheme1.reference == "ATE00001"
        (bid_status_revision1,) = scheme1.funding.bid_status_revisions
        assert bid_status_revision1.status == BidStatus.FUNDED

    @respx.mock
    async def test_get_by_authority_sets_authority_review(
        self, access_token: str, api_base_url: str, schemes: ApiSchemeRepository
    ) -> None:
        respx.get(f"{api_base_url}/funding-programmes", headers={"Authorization": f"Bearer {access_token}"}).mock(
            return_value=Response(200, json=_dummy_funding_programmes_json())
        )
        respx.get(
            f"{api_base_url}/capital-schemes/milestones", headers={"Authorization": f"Bearer {access_token}"}
        ).mock(return_value=Response(200, json=_dummy_milestones_json()))
        respx.get(
            f"{api_base_url}/authorities/LIV/capital-schemes/bid-submitting",
            headers={"Authorization": f"Bearer {access_token}"},
        ).mock(return_value=Response(200, json={"items": [f"{api_base_url}/capital-schemes/ATE00001"]}))
        respx.get(f"{api_base_url}/capital-schemes/ATE00001", headers={"Authorization": f"Bearer {access_token}"}).mock(
            return_value=Response(
                200,
                json={
                    "reference": "ATE00001",
                    "overview": _dummy_overview_json(),
                    "bidStatusDetails": _dummy_bid_status_details_json(),
                    "authorityReview": {"reviewDate": "2020-01-02T00:00:00Z"},
                },
            )
        )

        (scheme1,) = await schemes.get_by_authority("LIV")

        assert scheme1.reference == "ATE00001"
        (authority_review1,) = scheme1.reviews.authority_reviews
        assert authority_review1.review_date == datetime(2020, 1, 2)

    @respx.mock
    async def test_get_by_authority_filters_by_funding_programme_eligible_for_authority_update(
        self, access_token: str, api_base_url: str, schemes: ApiSchemeRepository
    ) -> None:
        respx.get(
            f"{api_base_url}/funding-programmes",
            params={"eligible-for-authority-update": "true"},
            headers={"Authorization": f"Bearer {access_token}"},
        ).mock(
            return_value=Response(
                200,
                json={
                    "items": [
                        {"@id": f"{api_base_url}/funding-programmes/ATF3", "code": "ATF3"},
                        {"@id": f"{api_base_url}/funding-programmes/ATF4", "code": "ATF4"},
                    ]
                },
            )
        )
        respx.get(
            f"{api_base_url}/capital-schemes/milestones", headers={"Authorization": f"Bearer {access_token}"}
        ).mock(return_value=Response(200, json=_dummy_milestones_json()))
        respx.get(
            f"{api_base_url}/authorities/LIV/capital-schemes/bid-submitting",
            params={"funding-programme-code": ["ATF3", "ATF4"]},
            headers={"Authorization": f"Bearer {access_token}"},
        ).mock(return_value=Response(200, json={"items": [f"{api_base_url}/capital-schemes/ATE00001"]}))
        respx.get(f"{api_base_url}/capital-schemes/ATE00001", headers={"Authorization": f"Bearer {access_token}"}).mock(
            return_value=Response(
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
        )

        (scheme1,) = await schemes.get_by_authority("LIV")

        assert scheme1.reference == "ATE00001"

    @respx.mock
    async def test_get_by_authority_filters_by_bid_status_funded(
        self, access_token: str, api_base_url: str, schemes: ApiSchemeRepository
    ) -> None:
        respx.get(f"{api_base_url}/funding-programmes", headers={"Authorization": f"Bearer {access_token}"}).mock(
            return_value=Response(200, json=_dummy_funding_programmes_json())
        )
        respx.get(
            f"{api_base_url}/capital-schemes/milestones", headers={"Authorization": f"Bearer {access_token}"}
        ).mock(return_value=Response(200, json=_dummy_milestones_json()))
        respx.get(
            f"{api_base_url}/authorities/LIV/capital-schemes/bid-submitting",
            params={"bid-status": "funded"},
            headers={"Authorization": f"Bearer {access_token}"},
        ).mock(return_value=Response(200, json={"items": [f"{api_base_url}/capital-schemes/ATE00001"]}))
        respx.get(f"{api_base_url}/capital-schemes/ATE00001", headers={"Authorization": f"Bearer {access_token}"}).mock(
            return_value=Response(200, json=_build_capital_scheme_json("ATE00001"))
        )

        (scheme1,) = await schemes.get_by_authority("LIV")

        assert scheme1.reference == "ATE00001"

    @respx.mock
    async def test_get_by_authority_filters_by_current_milestone_active_and_incomplete(
        self, access_token: str, api_base_url: str, schemes: ApiSchemeRepository
    ) -> None:
        respx.get(f"{api_base_url}/funding-programmes", headers={"Authorization": f"Bearer {access_token}"}).mock(
            return_value=Response(200, json=_dummy_funding_programmes_json())
        )
        respx.get(
            f"{api_base_url}/capital-schemes/milestones",
            params={"active": "true", "complete": "false"},
            headers={"Authorization": f"Bearer {access_token}"},
        ).mock(return_value=Response(200, json={"items": ["detailed design completed", "construction started"]}))
        respx.get(
            f"{api_base_url}/authorities/LIV/capital-schemes/bid-submitting",
            params={"current-milestone": ["detailed design completed", "construction started", ""]},
            headers={"Authorization": f"Bearer {access_token}"},
        ).mock(return_value=Response(200, json={"items": [f"{api_base_url}/capital-schemes/ATE00001"]}))
        respx.get(f"{api_base_url}/capital-schemes/ATE00001", headers={"Authorization": f"Bearer {access_token}"}).mock(
            return_value=Response(200, json=_build_capital_scheme_json("ATE00001"))
        )

        (scheme1,) = await schemes.get_by_authority("LIV")

        assert scheme1.reference == "ATE00001"

    @respx.mock
    async def test_get_by_authority_reuses_client(
        self, api_base_url: str, remote_app: StubRemoteApp, schemes: ApiSchemeRepository
    ) -> None:
        respx.get(f"{api_base_url}/funding-programmes").mock(
            return_value=Response(200, json=_dummy_funding_programmes_json())
        )
        respx.get(f"{api_base_url}/capital-schemes/milestones").mock(
            return_value=Response(200, json=_dummy_milestones_json())
        )
        respx.get(f"{api_base_url}/authorities/LIV/capital-schemes/bid-submitting").mock(
            return_value=Response(
                200,
                json={
                    "items": [
                        f"{api_base_url}/capital-schemes/ATE00001",
                        f"{api_base_url}/capital-schemes/ATE00002",
                    ]
                },
            )
        )
        respx.get(f"{api_base_url}/capital-schemes/ATE00001").mock(
            return_value=Response(200, json=_build_capital_scheme_json("ATE00001"))
        )
        respx.get(f"{api_base_url}/capital-schemes/ATE00002").mock(
            return_value=Response(200, json=_build_capital_scheme_json("ATE00002"))
        )

        await schemes.get_by_authority("LIV")

        assert remote_app.client_count == 1


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
