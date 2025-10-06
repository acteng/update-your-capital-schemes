from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any

import pytest
from pydantic import AnyUrl
from respx import MockRouter

from schemes.domain.schemes.funding import BidStatus, FinancialType
from schemes.domain.schemes.milestones import Milestone
from schemes.domain.schemes.observations import ObservationType
from schemes.domain.schemes.outputs import OutputTypeMeasure
from schemes.domain.schemes.overview import FundingProgrammes
from schemes.infrastructure.api.authorities import AuthorityModel
from schemes.infrastructure.api.collections import CollectionModel
from schemes.infrastructure.api.funding_programmes import FundingProgrammeItemModel
from schemes.infrastructure.api.observation_types import ObservationTypeModel
from schemes.infrastructure.api.schemes.bid_statuses import BidStatusModel, CapitalSchemeBidStatusDetailsModel
from schemes.infrastructure.api.schemes.financials import CapitalSchemeFinancialModel, FinancialTypeModel
from schemes.infrastructure.api.schemes.milestones import CapitalSchemeMilestoneModel, MilestoneModel
from schemes.infrastructure.api.schemes.outputs import CapitalSchemeOutputModel, OutputMeasureModel, OutputTypeModel
from schemes.infrastructure.api.schemes.overviews import CapitalSchemeOverviewModel, CapitalSchemeTypeModel
from schemes.infrastructure.api.schemes.schemes import (
    ApiSchemeRepository,
    CapitalSchemeAuthorityReviewModel,
    CapitalSchemeModel,
)
from schemes.oauth import ClientAsyncBaseApp
from tests.infrastructure.api.conftest import StubRemoteApp


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
        authority_model = AuthorityModel(
            id=AnyUrl("https://api.example/authorities/LIV"),
            abbreviation="LIV",
            full_name="Liverpool City Region Combined Authority",
            bid_submitting_capital_schemes=AnyUrl("https://api.example/authorities/LIV/capital-schemes/bid-submitting"),
        )
        funding_programme_item_model = FundingProgrammeItemModel(
            id=AnyUrl("https://api.example/funding-programmes/ATF4"), code="ATF4"
        )
        capital_scheme_model = CapitalSchemeModel(
            reference="ATE00001",
            overview=CapitalSchemeOverviewModel(
                name="Wirral Package",
                bid_submitting_authority=AnyUrl("https://api.example/authorities/LIV"),
                funding_programme=AnyUrl("https://api.example/funding-programmes/ATF4"),
                type=CapitalSchemeTypeModel.CONSTRUCTION,
            ),
            financials=CollectionModel[CapitalSchemeFinancialModel](items=[]),
            milestones=CollectionModel[CapitalSchemeMilestoneModel](items=[]),
            outputs=CollectionModel[CapitalSchemeOutputModel](items=[]),
            bid_status_details=CapitalSchemeBidStatusDetailsModel(bid_status=BidStatusModel.FUNDED),
        )

        scheme = capital_scheme_model.to_domain([authority_model], [funding_programme_item_model])

        assert scheme.reference == "ATE00001"
        (overview_revision1,) = scheme.overview.overview_revisions
        assert (
            overview_revision1.name == "Wirral Package"
            and overview_revision1.authority_abbreviation == "LIV"
            and overview_revision1.funding_programme == FundingProgrammes.ATF4
        )
        (bid_status_revision1,) = scheme.funding.bid_status_revisions
        assert bid_status_revision1.status == BidStatus.FUNDED
        assert not scheme.funding.financial_revisions
        assert not scheme.milestones.milestone_revisions
        assert not scheme.outputs.output_revisions
        assert not scheme.reviews.authority_reviews

    def test_to_domain_sets_financial_revisions(self) -> None:
        capital_scheme_model = CapitalSchemeModel(
            reference="ATE00001",
            overview=_dummy_overview_model(),
            bid_status_details=_dummy_bid_status_details_model(),
            financials=CollectionModel[CapitalSchemeFinancialModel](
                items=[
                    CapitalSchemeFinancialModel(type=FinancialTypeModel.FUNDING_ALLOCATION, amount=100_000),
                    CapitalSchemeFinancialModel(type=FinancialTypeModel.SPEND_TO_DATE, amount=50_000),
                ]
            ),
            milestones=CollectionModel[CapitalSchemeMilestoneModel](items=[]),
            outputs=CollectionModel[CapitalSchemeOutputModel](items=[]),
        )

        scheme = capital_scheme_model.to_domain([_dummy_authority_model()], [_dummy_funding_programme_item_model()])

        assert scheme.reference == "ATE00001"
        (financial_revision1, financial_revision2) = scheme.funding.financial_revisions
        assert financial_revision1.type == FinancialType.FUNDING_ALLOCATION and financial_revision1.amount == 100_000
        assert financial_revision2.type == FinancialType.SPEND_TO_DATE and financial_revision2.amount == 50_000

    def test_to_domain_sets_milestone_revisions(self) -> None:
        capital_scheme_model = CapitalSchemeModel(
            reference="ATE00001",
            overview=_dummy_overview_model(),
            bid_status_details=_dummy_bid_status_details_model(),
            financials=CollectionModel[CapitalSchemeFinancialModel](items=[]),
            milestones=CollectionModel[CapitalSchemeMilestoneModel](
                items=[
                    CapitalSchemeMilestoneModel(
                        milestone=MilestoneModel.DETAILED_DESIGN_COMPLETED,
                        observation_type=ObservationTypeModel.PLANNED,
                        status_date=date(2020, 2, 1),
                    ),
                    CapitalSchemeMilestoneModel(
                        milestone=MilestoneModel.CONSTRUCTION_STARTED,
                        observation_type=ObservationTypeModel.PLANNED,
                        status_date=date(2020, 3, 1),
                    ),
                ]
            ),
            outputs=CollectionModel[CapitalSchemeOutputModel](items=[]),
        )

        scheme = capital_scheme_model.to_domain([_dummy_authority_model()], [_dummy_funding_programme_item_model()])

        assert scheme.reference == "ATE00001"
        (milestone_revision1, milestone_revision2) = scheme.milestones.milestone_revisions
        assert (
            milestone_revision1.milestone == Milestone.DETAILED_DESIGN_COMPLETED
            and milestone_revision1.observation_type == ObservationType.PLANNED
            and milestone_revision1.status_date == date(2020, 2, 1)
        )
        assert (
            milestone_revision2.milestone == Milestone.CONSTRUCTION_STARTED
            and milestone_revision2.observation_type == ObservationType.PLANNED
            and milestone_revision2.status_date == date(2020, 3, 1)
        )

    def test_to_domain_sets_output_revisions(self) -> None:
        capital_scheme_model = CapitalSchemeModel(
            reference="ATE00001",
            overview=_dummy_overview_model(),
            bid_status_details=_dummy_bid_status_details_model(),
            financials=CollectionModel[CapitalSchemeFinancialModel](items=[]),
            milestones=CollectionModel[CapitalSchemeMilestoneModel](items=[]),
            outputs=CollectionModel[CapitalSchemeOutputModel](
                items=[
                    CapitalSchemeOutputModel(
                        type=OutputTypeModel.WIDENING_EXISTING_FOOTWAY,
                        measure=OutputMeasureModel.MILES,
                        observation_type=ObservationTypeModel.ACTUAL,
                        value=Decimal(1.5),
                    ),
                    CapitalSchemeOutputModel(
                        type=OutputTypeModel.NEW_SEGREGATED_CYCLING_FACILITY,
                        measure=OutputMeasureModel.MILES,
                        observation_type=ObservationTypeModel.ACTUAL,
                        value=Decimal(2),
                    ),
                ]
            ),
        )

        scheme = capital_scheme_model.to_domain([_dummy_authority_model()], [_dummy_funding_programme_item_model()])

        assert scheme.reference == "ATE00001"
        (output_revision1, output_revision2) = scheme.outputs.output_revisions
        assert (
            output_revision1.type_measure == OutputTypeMeasure.WIDENING_EXISTING_FOOTWAY_MILES
            and output_revision1.observation_type == ObservationType.ACTUAL
            and output_revision1.value == Decimal(1.5)
        )
        assert (
            output_revision2.type_measure == OutputTypeMeasure.NEW_SEGREGATED_CYCLING_FACILITY_MILES
            and output_revision2.observation_type == ObservationType.ACTUAL
            and output_revision2.value == Decimal(2)
        )

    def test_to_domain_sets_authority_review(self) -> None:
        capital_scheme_model = CapitalSchemeModel(
            reference="ATE00001",
            overview=_dummy_overview_model(),
            bid_status_details=_dummy_bid_status_details_model(),
            financials=CollectionModel[CapitalSchemeFinancialModel](items=[]),
            milestones=CollectionModel[CapitalSchemeMilestoneModel](items=[]),
            outputs=CollectionModel[CapitalSchemeOutputModel](items=[]),
            authority_review=CapitalSchemeAuthorityReviewModel(review_date=datetime(2020, 1, 2)),
        )

        scheme = capital_scheme_model.to_domain([_dummy_authority_model()], [_dummy_funding_programme_item_model()])

        assert scheme.reference == "ATE00001"
        (authority_review1,) = scheme.reviews.authority_reviews
        assert authority_review1.review_date == datetime(2020, 1, 2)


class TestApiSchemeRepository:
    @pytest.fixture(name="schemes")
    def schemes_fixture(self, remote_app: ClientAsyncBaseApp) -> ApiSchemeRepository:
        return ApiSchemeRepository(remote_app)

    async def test_get_scheme(self, api_mock: MockRouter, schemes: ApiSchemeRepository) -> None:
        api_mock.get(_build_funding_programme_json()["@id"]).respond(200, json=_build_funding_programme_json())
        api_mock.get(_build_authority_json()["@id"]).respond(200, json=_build_authority_json())
        api_mock.get("/capital-schemes/ATE00001").respond(200, json=_build_capital_scheme_json(reference="ATE00001"))

        scheme = await schemes.get("ATE00001")

        assert scheme and scheme.reference == "ATE00001"

    async def test_get_scheme_sets_overview_revision(
        self, api_mock: MockRouter, api_base_url: str, schemes: ApiSchemeRepository
    ) -> None:
        api_mock.get("/funding-programmes/ATF4").respond(
            200, json=_build_funding_programme_json(id_=f"{api_base_url}/funding-programmes/ATF4", code="ATF4")
        )
        api_mock.get("/authorities/LIV").respond(
            200, json=_build_authority_json(id_=f"{api_base_url}/authorities/LIV", abbreviation="LIV")
        )
        api_mock.get("/capital-schemes/ATE00001").respond(
            200,
            json=_build_capital_scheme_json(
                reference="ATE00001",
                name="Wirral Package",
                bid_submitting_authority=f"{api_base_url}/authorities/LIV",
                funding_programme=f"{api_base_url}/funding-programmes/ATF4",
            ),
        )

        scheme = await schemes.get("ATE00001")

        assert scheme and scheme.reference == "ATE00001"
        (overview_revision1,) = scheme.overview.overview_revisions
        assert (
            overview_revision1.name == "Wirral Package"
            and overview_revision1.authority_abbreviation == "LIV"
            and overview_revision1.funding_programme == FundingProgrammes.ATF4
        )

    async def test_get_scheme_sets_bid_status_revision(
        self, api_mock: MockRouter, api_base_url: str, schemes: ApiSchemeRepository
    ) -> None:
        api_mock.get(_build_funding_programme_json()["@id"]).respond(200, json=_build_funding_programme_json())
        api_mock.get(_build_authority_json()["@id"]).respond(200, json=_build_authority_json())
        api_mock.get("/capital-schemes/ATE00001").respond(
            200, json=_build_capital_scheme_json(reference="ATE00001", bid_status="funded")
        )

        scheme = await schemes.get("ATE00001")

        assert scheme and scheme.reference == "ATE00001"
        (bid_status_revision1,) = scheme.funding.bid_status_revisions
        assert bid_status_revision1.status == BidStatus.FUNDED

    async def test_get_scheme_sets_financial_revisions(
        self, api_mock: MockRouter, api_base_url: str, schemes: ApiSchemeRepository
    ) -> None:
        api_mock.get(_build_funding_programme_json()["@id"]).respond(200, json=_build_funding_programme_json())
        api_mock.get(_build_authority_json()["@id"]).respond(200, json=_build_authority_json())
        api_mock.get("/capital-schemes/ATE00001").respond(
            200,
            json=_build_capital_scheme_json(
                reference="ATE00001",
                financials=[
                    _build_financial_json(type_="funding allocation", amount=100_000),
                    _build_financial_json(type_="spend to date", amount=50_000),
                ],
            ),
        )

        scheme = await schemes.get("ATE00001")

        assert scheme and scheme.reference == "ATE00001"
        (financial_revision1, financial_revision2) = scheme.funding.financial_revisions
        assert financial_revision1.type == FinancialType.FUNDING_ALLOCATION and financial_revision1.amount == 100_000
        assert financial_revision2.type == FinancialType.SPEND_TO_DATE and financial_revision2.amount == 50_000

    async def test_get_scheme_sets_milestone_revisions(
        self, api_mock: MockRouter, api_base_url: str, schemes: ApiSchemeRepository
    ) -> None:
        api_mock.get(_build_funding_programme_json()["@id"]).respond(200, json=_build_funding_programme_json())
        api_mock.get(_build_authority_json()["@id"]).respond(200, json=_build_authority_json())
        api_mock.get("/capital-schemes/ATE00001").respond(
            200,
            json=_build_capital_scheme_json(
                reference="ATE00001",
                milestones=[
                    _build_milestone_json(
                        milestone="detailed design completed", observation_type="planned", status_date="2020-02-01"
                    ),
                    _build_milestone_json(
                        milestone="construction started", observation_type="planned", status_date="2020-03-01"
                    ),
                ],
            ),
        )

        scheme = await schemes.get("ATE00001")

        assert scheme and scheme.reference == "ATE00001"
        (milestone_revision1, milestone_revision2) = scheme.milestones.milestone_revisions
        assert (
            milestone_revision1.milestone == Milestone.DETAILED_DESIGN_COMPLETED
            and milestone_revision1.observation_type == ObservationType.PLANNED
            and milestone_revision1.status_date == date(2020, 2, 1)
        )
        assert (
            milestone_revision2.milestone == Milestone.CONSTRUCTION_STARTED
            and milestone_revision2.observation_type == ObservationType.PLANNED
            and milestone_revision2.status_date == date(2020, 3, 1)
        )

    async def test_get_scheme_sets_output_revisions(
        self, api_mock: MockRouter, api_base_url: str, schemes: ApiSchemeRepository
    ) -> None:
        api_mock.get(_build_funding_programme_json()["@id"]).respond(200, json=_build_funding_programme_json())
        api_mock.get(_build_authority_json()["@id"]).respond(200, json=_build_authority_json())
        api_mock.get("/capital-schemes/ATE00001").respond(
            200,
            json=_build_capital_scheme_json(
                reference="ATE00001",
                outputs=[
                    _build_output_json(
                        type_="widening existing footway", measure="miles", observation_type="actual", value="1.500000"
                    ),
                    _build_output_json(
                        type_="new segregated cycling facility",
                        measure="miles",
                        observation_type="actual",
                        value="2.000000",
                    ),
                ],
            ),
        )

        scheme = await schemes.get("ATE00001")

        assert scheme and scheme.reference == "ATE00001"
        (output_revision1, output_revision2) = scheme.outputs.output_revisions
        assert (
            output_revision1.type_measure == OutputTypeMeasure.WIDENING_EXISTING_FOOTWAY_MILES
            and output_revision1.observation_type == ObservationType.ACTUAL
            and output_revision1.value == Decimal(1.5)
        )
        assert (
            output_revision2.type_measure == OutputTypeMeasure.NEW_SEGREGATED_CYCLING_FACILITY_MILES
            and output_revision2.observation_type == ObservationType.ACTUAL
            and output_revision2.value == Decimal(2)
        )

    async def test_get_scheme_sets_authority_review(
        self, api_mock: MockRouter, api_base_url: str, schemes: ApiSchemeRepository
    ) -> None:
        api_mock.get(_build_funding_programme_json()["@id"]).respond(200, json=_build_funding_programme_json())
        api_mock.get(_build_authority_json()["@id"]).respond(200, json=_build_authority_json())
        api_mock.get("/capital-schemes/ATE00001").respond(
            200, json=_build_capital_scheme_json(reference="ATE00001", review_date="2020-01-02T00:00:00Z")
        )

        scheme = await schemes.get("ATE00001")

        assert scheme and scheme.reference == "ATE00001"
        (authority_review1,) = scheme.reviews.authority_reviews
        assert authority_review1.review_date == datetime(2020, 1, 2)

    async def test_get_scheme_ignores_unknown_key(self, api_mock: MockRouter, schemes: ApiSchemeRepository) -> None:
        api_mock.get(_build_funding_programme_json()["@id"]).respond(200, json=_build_funding_programme_json())
        api_mock.get(_build_authority_json()["@id"]).respond(200, json=_build_authority_json())
        api_mock.get("/capital-schemes/ATE00001").respond(
            200, json=_build_capital_scheme_json("ATE00001") | {"foo": "bar"}
        )

        scheme = await schemes.get("ATE00001")

        assert scheme and scheme.reference == "ATE00001"

    async def test_get_scheme_that_does_not_exist(self, api_mock: MockRouter, schemes: ApiSchemeRepository) -> None:
        api_mock.get("/capital-schemes/ATE00001").respond(404)

        assert await schemes.get("ATE00001") is None

    async def test_get_scheme_reuses_client(
        self, api_mock: MockRouter, remote_app: StubRemoteApp, schemes: ApiSchemeRepository
    ) -> None:
        api_mock.get(_build_funding_programme_json()["@id"]).respond(200, json=_build_funding_programme_json())
        api_mock.get(_build_authority_json()["@id"]).respond(200, json=_build_authority_json())
        api_mock.get("/capital-schemes/ATE00001").respond(200, json=_build_capital_scheme_json("ATE00001"))

        await schemes.get("ATE00001")

        assert remote_app.client_count == 1

    async def test_get_schemes_by_authority(
        self, api_mock: MockRouter, api_base_url: str, schemes: ApiSchemeRepository
    ) -> None:
        api_mock.get("/funding-programmes").respond(200, json={"items": [_build_funding_programme_item_json()]})
        api_mock.get("/capital-schemes/milestones").respond(200, json={"items": []})
        api_mock.get("/authorities/LIV").respond(
            200,
            json=_build_authority_json(
                id_=f"{api_base_url}/authorities/LIV",
                abbreviation="LIV",
                bid_submitting_capital_schemes=f"{api_base_url}/authorities/LIV/capital-schemes/bid-submitting",
            ),
        )
        api_mock.get("/authorities/LIV/capital-schemes/bid-submitting").respond(
            200,
            json={"items": [f"{api_base_url}/capital-schemes/ATE00001", f"{api_base_url}/capital-schemes/ATE00002"]},
        )
        api_mock.get("/capital-schemes/ATE00001").respond(
            200,
            json=_build_capital_scheme_json(
                reference="ATE00001", bid_submitting_authority=f"{api_base_url}/authorities/LIV"
            ),
        )
        api_mock.get("/capital-schemes/ATE00002").respond(
            200,
            json=_build_capital_scheme_json(
                reference="ATE00002", bid_submitting_authority=f"{api_base_url}/authorities/LIV"
            ),
        )

        scheme1, scheme2 = await schemes.get_by_authority("LIV")

        assert scheme1.reference == "ATE00001"
        assert scheme2.reference == "ATE00002"

    async def test_get_schemes_by_authority_sets_overview_revision(
        self, api_mock: MockRouter, api_base_url: str, schemes: ApiSchemeRepository
    ) -> None:
        api_mock.get("/funding-programmes").respond(
            200,
            json={
                "items": [
                    _build_funding_programme_item_json(id_=f"{api_base_url}/funding-programmes/ATF4", code="ATF4")
                ]
            },
        )
        api_mock.get("/capital-schemes/milestones").respond(200, json={"items": []})
        api_mock.get("/authorities/LIV").respond(
            200,
            json=_build_authority_json(
                id_=f"{api_base_url}/authorities/LIV",
                abbreviation="LIV",
                bid_submitting_capital_schemes=f"{api_base_url}/authorities/LIV/capital-schemes/bid-submitting",
            ),
        )
        api_mock.get("/authorities/LIV/capital-schemes/bid-submitting").respond(
            200, json={"items": [f"{api_base_url}/capital-schemes/ATE00001"]}
        )
        api_mock.get("/capital-schemes/ATE00001").respond(
            200,
            json=_build_capital_scheme_json(
                reference="ATE00001",
                name="Wirral Package",
                bid_submitting_authority=f"{api_base_url}/authorities/LIV",
                funding_programme=f"{api_base_url}/funding-programmes/ATF4",
            ),
        )

        (scheme1,) = await schemes.get_by_authority("LIV")

        assert scheme1.reference == "ATE00001"
        (overview_revision1,) = scheme1.overview.overview_revisions
        assert (
            overview_revision1.name == "Wirral Package"
            and overview_revision1.authority_abbreviation == "LIV"
            and overview_revision1.funding_programme == FundingProgrammes.ATF4
        )

    async def test_get_schemes_by_authority_sets_bid_status_revision(
        self, api_mock: MockRouter, api_base_url: str, schemes: ApiSchemeRepository
    ) -> None:
        api_mock.get("/funding-programmes").respond(200, json={"items": [_build_funding_programme_item_json()]})
        api_mock.get("/capital-schemes/milestones").respond(200, json={"items": []})
        api_mock.get("/authorities/LIV").respond(
            200,
            json=_build_authority_json(
                id_=f"{api_base_url}/authorities/LIV",
                abbreviation="LIV",
                bid_submitting_capital_schemes=f"{api_base_url}/authorities/LIV/capital-schemes/bid-submitting",
            ),
        )
        api_mock.get("/authorities/LIV/capital-schemes/bid-submitting").respond(
            200, json={"items": [f"{api_base_url}/capital-schemes/ATE00001"]}
        )
        api_mock.get("/capital-schemes/ATE00001").respond(
            200,
            json=_build_capital_scheme_json(
                reference="ATE00001", bid_submitting_authority=f"{api_base_url}/authorities/LIV", bid_status="funded"
            ),
        )

        (scheme1,) = await schemes.get_by_authority("LIV")

        assert scheme1.reference == "ATE00001"
        (bid_status_revision1,) = scheme1.funding.bid_status_revisions
        assert bid_status_revision1.status == BidStatus.FUNDED

    async def test_get_schemes_by_authority_sets_financial_revisions(
        self, api_mock: MockRouter, api_base_url: str, schemes: ApiSchemeRepository
    ) -> None:
        api_mock.get("/funding-programmes").respond(200, json={"items": [_build_funding_programme_item_json()]})
        api_mock.get("/capital-schemes/milestones").respond(200, json={"items": []})
        api_mock.get("/authorities/LIV").respond(
            200,
            json=_build_authority_json(
                id_=f"{api_base_url}/authorities/LIV",
                abbreviation="LIV",
                bid_submitting_capital_schemes=f"{api_base_url}/authorities/LIV/capital-schemes/bid-submitting",
            ),
        )
        api_mock.get("/authorities/LIV/capital-schemes/bid-submitting").respond(
            200, json={"items": [f"{api_base_url}/capital-schemes/ATE00001"]}
        )
        api_mock.get("/capital-schemes/ATE00001").respond(
            200,
            json=_build_capital_scheme_json(
                reference="ATE00001",
                bid_submitting_authority=f"{api_base_url}/authorities/LIV",
                financials=[
                    _build_financial_json(type_="funding allocation", amount=100_000),
                    _build_financial_json(type_="spend to date", amount=50_000),
                ],
            ),
        )

        (scheme1,) = await schemes.get_by_authority("LIV")

        assert scheme1.reference == "ATE00001"
        (financial_revision1, financial_revision2) = scheme1.funding.financial_revisions
        assert financial_revision1.type == FinancialType.FUNDING_ALLOCATION and financial_revision1.amount == 100_000
        assert financial_revision2.type == FinancialType.SPEND_TO_DATE and financial_revision2.amount == 50_000

    async def test_get_schemes_by_authority_sets_milestone_revisions(
        self, api_mock: MockRouter, api_base_url: str, schemes: ApiSchemeRepository
    ) -> None:
        api_mock.get("/funding-programmes").respond(200, json={"items": [_build_funding_programme_item_json()]})
        api_mock.get("/capital-schemes/milestones").respond(200, json={"items": []})
        api_mock.get("/authorities/LIV").respond(
            200,
            json=_build_authority_json(
                id_=f"{api_base_url}/authorities/LIV",
                abbreviation="LIV",
                bid_submitting_capital_schemes=f"{api_base_url}/authorities/LIV/capital-schemes/bid-submitting",
            ),
        )
        api_mock.get("/authorities/LIV/capital-schemes/bid-submitting").respond(
            200, json={"items": [f"{api_base_url}/capital-schemes/ATE00001"]}
        )
        api_mock.get("/capital-schemes/ATE00001").respond(
            200,
            json=_build_capital_scheme_json(
                reference="ATE00001",
                bid_submitting_authority=f"{api_base_url}/authorities/LIV",
                milestones=[
                    _build_milestone_json(
                        milestone="detailed design completed", observation_type="planned", status_date="2020-02-01"
                    ),
                    _build_milestone_json(
                        milestone="construction started", observation_type="planned", status_date="2020-03-01"
                    ),
                ],
            ),
        )

        (scheme1,) = await schemes.get_by_authority("LIV")

        assert scheme1.reference == "ATE00001"
        (milestone_revision1, milestone_revision2) = scheme1.milestones.milestone_revisions
        assert (
            milestone_revision1.milestone == Milestone.DETAILED_DESIGN_COMPLETED
            and milestone_revision1.observation_type == ObservationType.PLANNED
            and milestone_revision1.status_date == date(2020, 2, 1)
        )
        assert (
            milestone_revision2.milestone == Milestone.CONSTRUCTION_STARTED
            and milestone_revision2.observation_type == ObservationType.PLANNED
            and milestone_revision2.status_date == date(2020, 3, 1)
        )

    async def test_get_schemes_by_authority_sets_output_revisions(
        self, api_mock: MockRouter, api_base_url: str, schemes: ApiSchemeRepository
    ) -> None:
        api_mock.get("/funding-programmes").respond(200, json={"items": [_build_funding_programme_item_json()]})
        api_mock.get("/capital-schemes/milestones").respond(200, json={"items": []})
        api_mock.get("/authorities/LIV").respond(
            200,
            json=_build_authority_json(
                id_=f"{api_base_url}/authorities/LIV",
                abbreviation="LIV",
                bid_submitting_capital_schemes=f"{api_base_url}/authorities/LIV/capital-schemes/bid-submitting",
            ),
        )
        api_mock.get("/authorities/LIV/capital-schemes/bid-submitting").respond(
            200, json={"items": [f"{api_base_url}/capital-schemes/ATE00001"]}
        )
        api_mock.get("/capital-schemes/ATE00001").respond(
            200,
            json=_build_capital_scheme_json(
                reference="ATE00001",
                bid_submitting_authority=f"{api_base_url}/authorities/LIV",
                outputs=[
                    _build_output_json(
                        type_="widening existing footway", measure="miles", observation_type="actual", value="1.500000"
                    ),
                    _build_output_json(
                        type_="new segregated cycling facility",
                        measure="miles",
                        observation_type="actual",
                        value="2.000000",
                    ),
                ],
            ),
        )

        (scheme1,) = await schemes.get_by_authority("LIV")

        assert scheme1.reference == "ATE00001"
        (output_revision1, output_revision2) = scheme1.outputs.output_revisions
        assert (
            output_revision1.type_measure == OutputTypeMeasure.WIDENING_EXISTING_FOOTWAY_MILES
            and output_revision1.observation_type == ObservationType.ACTUAL
            and output_revision1.value == Decimal(1.5)
        )
        assert (
            output_revision2.type_measure == OutputTypeMeasure.NEW_SEGREGATED_CYCLING_FACILITY_MILES
            and output_revision2.observation_type == ObservationType.ACTUAL
            and output_revision2.value == Decimal(2)
        )

    async def test_get_schemes_by_authority_sets_authority_review(
        self, api_mock: MockRouter, api_base_url: str, schemes: ApiSchemeRepository
    ) -> None:
        api_mock.get("/funding-programmes").respond(200, json={"items": [_build_funding_programme_item_json()]})
        api_mock.get("/capital-schemes/milestones").respond(200, json={"items": []})
        api_mock.get("/authorities/LIV").respond(
            200,
            json=_build_authority_json(
                id_=f"{api_base_url}/authorities/LIV",
                abbreviation="LIV",
                bid_submitting_capital_schemes=f"{api_base_url}/authorities/LIV/capital-schemes/bid-submitting",
            ),
        )
        api_mock.get("/authorities/LIV/capital-schemes/bid-submitting").respond(
            200, json={"items": [f"{api_base_url}/capital-schemes/ATE00001"]}
        )
        api_mock.get("/capital-schemes/ATE00001").respond(
            200,
            json=_build_capital_scheme_json(
                reference="ATE00001",
                bid_submitting_authority=f"{api_base_url}/authorities/LIV",
                review_date="2020-01-02T00:00:00Z",
            ),
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
                    _build_funding_programme_item_json(id_=f"{api_base_url}/funding-programmes/ATF3", code="ATF3"),
                    _build_funding_programme_item_json(id_=f"{api_base_url}/funding-programmes/ATF4", code="ATF4"),
                ]
            },
        )
        api_mock.get("/capital-schemes/milestones").respond(200, json={"items": []})
        api_mock.get("/authorities/LIV").respond(
            200,
            json=_build_authority_json(
                id_=f"{api_base_url}/authorities/LIV",
                abbreviation="LIV",
                bid_submitting_capital_schemes=f"{api_base_url}/authorities/LIV/capital-schemes/bid-submitting",
            ),
        )
        api_mock.get(
            "/authorities/LIV/capital-schemes/bid-submitting", params={"funding-programme-code": ["ATF3", "ATF4"]}
        ).respond(200, json={"items": [f"{api_base_url}/capital-schemes/ATE00001"]})
        api_mock.get("/capital-schemes/ATE00001").respond(
            200,
            json=_build_capital_scheme_json(
                reference="ATE00001",
                bid_submitting_authority=f"{api_base_url}/authorities/LIV",
                funding_programme=f"{api_base_url}/funding-programmes/ATF4",
            ),
        )

        (scheme1,) = await schemes.get_by_authority("LIV")

        assert scheme1.reference == "ATE00001"

    async def test_get_schemes_by_authority_filters_by_bid_status_funded(
        self, api_mock: MockRouter, api_base_url: str, schemes: ApiSchemeRepository
    ) -> None:
        api_mock.get("/funding-programmes").respond(200, json={"items": [_build_funding_programme_item_json()]})
        api_mock.get("/capital-schemes/milestones").respond(200, json={"items": []})
        api_mock.get("/authorities/LIV").respond(
            200,
            json=_build_authority_json(
                id_=f"{api_base_url}/authorities/LIV",
                abbreviation="LIV",
                bid_submitting_capital_schemes=f"{api_base_url}/authorities/LIV/capital-schemes/bid-submitting",
            ),
        )
        api_mock.get("/authorities/LIV/capital-schemes/bid-submitting", params={"bid-status": "funded"}).respond(
            200, json={"items": [f"{api_base_url}/capital-schemes/ATE00001"]}
        )
        api_mock.get("/capital-schemes/ATE00001").respond(
            200,
            json=_build_capital_scheme_json(
                reference="ATE00001", bid_submitting_authority=f"{api_base_url}/authorities/LIV"
            ),
        )

        (scheme1,) = await schemes.get_by_authority("LIV")

        assert scheme1.reference == "ATE00001"

    async def test_get_schemes_by_authority_filters_by_current_milestone_active_and_incomplete(
        self, api_mock: MockRouter, api_base_url: str, schemes: ApiSchemeRepository
    ) -> None:
        api_mock.get("/funding-programmes").respond(200, json={"items": [_build_funding_programme_item_json()]})
        api_mock.get("/capital-schemes/milestones", params={"active": "true", "complete": "false"}).respond(
            200, json={"items": ["detailed design completed", "construction started"]}
        )
        api_mock.get("/authorities/LIV").respond(
            200,
            json=_build_authority_json(
                id_=f"{api_base_url}/authorities/LIV",
                abbreviation="LIV",
                bid_submitting_capital_schemes=f"{api_base_url}/authorities/LIV/capital-schemes/bid-submitting",
            ),
        )
        api_mock.get(
            "/authorities/LIV/capital-schemes/bid-submitting",
            params={"current-milestone": ["detailed design completed", "construction started", ""]},
        ).respond(200, json={"items": [f"{api_base_url}/capital-schemes/ATE00001"]})
        api_mock.get("/capital-schemes/ATE00001").respond(
            200,
            json=_build_capital_scheme_json(
                reference="ATE00001", bid_submitting_authority=f"{api_base_url}/authorities/LIV"
            ),
        )

        (scheme1,) = await schemes.get_by_authority("LIV")

        assert scheme1.reference == "ATE00001"

    async def test_get_schemes_by_authority_reuses_client(
        self, api_mock: MockRouter, api_base_url: str, remote_app: StubRemoteApp, schemes: ApiSchemeRepository
    ) -> None:
        api_mock.get("/funding-programmes").respond(200, json={"items": [_build_funding_programme_item_json()]})
        api_mock.get("/capital-schemes/milestones").respond(200, json={"items": []})
        api_mock.get("/authorities/LIV").respond(
            200,
            json=_build_authority_json(
                id_=f"{api_base_url}/authorities/LIV",
                abbreviation="LIV",
                bid_submitting_capital_schemes=f"{api_base_url}/authorities/LIV/capital-schemes/bid-submitting",
            ),
        )
        api_mock.get("/authorities/LIV/capital-schemes/bid-submitting").respond(
            200,
            json={"items": [f"{api_base_url}/capital-schemes/ATE00001", f"{api_base_url}/capital-schemes/ATE00002"]},
        )
        api_mock.get("/capital-schemes/ATE00001").respond(
            200,
            json=_build_capital_scheme_json(
                reference="ATE00001", bid_submitting_authority=f"{api_base_url}/authorities/LIV"
            ),
        )
        api_mock.get("/capital-schemes/ATE00002").respond(
            200,
            json=_build_capital_scheme_json(
                reference="ATE00002", bid_submitting_authority=f"{api_base_url}/authorities/LIV"
            ),
        )

        await schemes.get_by_authority("LIV")

        assert remote_app.client_count == 1


def _dummy_funding_programme_item_model() -> FundingProgrammeItemModel:
    return FundingProgrammeItemModel(id=AnyUrl("https://api.example/funding-programmes/dummy"), code="dummy")


def _dummy_authority_model() -> AuthorityModel:
    return AuthorityModel(
        id=AnyUrl("https://api.example/authorities/dummy"),
        abbreviation="dummy",
        full_name="dummy",
        bid_submitting_capital_schemes=AnyUrl("https://api.example/authorities/dummy/capital-schemes/bid-submitting"),
    )


def _dummy_overview_model() -> CapitalSchemeOverviewModel:
    return CapitalSchemeOverviewModel(
        name="dummy",
        bid_submitting_authority=AnyUrl("https://api.example/authorities/dummy"),
        funding_programme=AnyUrl("https://api.example/funding-programmes/dummy"),
        type=CapitalSchemeTypeModel.DEVELOPMENT,
    )


def _dummy_bid_status_details_model() -> CapitalSchemeBidStatusDetailsModel:
    return CapitalSchemeBidStatusDetailsModel(bid_status=BidStatusModel.SUBMITTED)


def _build_funding_programme_json(id_: str | None = None, code: str | None = None) -> dict[str, Any]:
    return {"@id": id_ or "https://api.example/funding-programmes/dummy", "code": code or "dummy"}


def _build_funding_programme_item_json(id_: str | None = None, code: str | None = None) -> dict[str, Any]:
    return {"@id": id_ or "https://api.example/funding-programmes/dummy", "code": code or "dummy"}


def _build_authority_json(
    id_: str | None = None,
    abbreviation: str | None = None,
    full_name: str | None = None,
    bid_submitting_capital_schemes: str | None = None,
) -> dict[str, Any]:
    return {
        "@id": id_ or "https://api.example/authorities/dummy",
        "abbreviation": abbreviation or "dummy",
        "fullName": full_name or "dummy",
        "bidSubmittingCapitalSchemes": bid_submitting_capital_schemes
        or "https://api.example/authorities/dummy/capital-schemes/bid-submitting",
    }


def _build_overview_json(
    name: str | None = None,
    bid_submitting_authority: str | None = None,
    funding_programme: str | None = None,
    type_: str | None = None,
) -> dict[str, Any]:
    return {
        "name": name or "dummy",
        "bidSubmittingAuthority": bid_submitting_authority or "https://api.example/authorities/dummy",
        "fundingProgramme": funding_programme or "https://api.example/funding-programmes/dummy",
        "type": type_ or "development",
    }


def _build_bid_status_details_json(bid_status: str | None = None) -> dict[str, Any]:
    return {"bidStatus": bid_status or "submitted"}


def _build_financial_json(type_: str | None = None, amount: int | None = None) -> dict[str, Any]:
    return {"type": type_ or "expected cost", "amount": amount or 0}


def _build_milestone_json(
    milestone: str | None = None, observation_type: str | None = None, status_date: str | None = None
) -> dict[str, Any]:
    return {
        "milestone": milestone or "public consultation completed",
        "observationType": observation_type or "planned",
        "statusDate": status_date or "1970-01-01",
    }


def _build_output_json(
    type_: str | None = None, measure: str | None = None, observation_type: str | None = None, value: str | None = None
) -> dict[str, Any]:
    return {
        "type": type_ or "new segregated cycling facility",
        "measure": measure or "miles",
        "observationType": observation_type or "planned",
        "value": value or "0.000000",
    }


def _build_authority_review_json(review_date: str | None = None) -> dict[str, Any]:
    return {"reviewDate": review_date or "1970-01-01T00:00:00Z"}


def _build_capital_scheme_json(
    reference: str | None = None,
    name: str | None = None,
    bid_submitting_authority: str | None = None,
    funding_programme: str | None = None,
    bid_status: str | None = None,
    financials: list[dict[str, Any]] | None = None,
    milestones: list[dict[str, Any]] | None = None,
    outputs: list[dict[str, Any]] | None = None,
    review_date: str | None = None,
) -> dict[str, Any]:
    return {
        "reference": reference or "dummy",
        "overview": _build_overview_json(
            name=name, bid_submitting_authority=bid_submitting_authority, funding_programme=funding_programme
        ),
        "bidStatusDetails": _build_bid_status_details_json(bid_status=bid_status),
        "financials": {"items": financials or []},
        "milestones": {"items": milestones or []},
        "outputs": {"items": outputs or []},
        "authorityReview": _build_authority_review_json(review_date=review_date) if review_date else None,
    }
