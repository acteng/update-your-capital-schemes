import asyncio
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import AnyUrl

from schemes.domain.dates import DateRange
from schemes.domain.schemes.data_sources import DataSource
from schemes.domain.schemes.funding import BidStatus, BidStatusRevision, FinancialRevision, FinancialType
from schemes.domain.schemes.milestones import Milestone, MilestoneRevision
from schemes.domain.schemes.outputs import OutputMeasure, OutputRevision, OutputType, OutputTypeMeasure
from schemes.domain.schemes.reviews import AuthorityReview
from schemes.domain.schemes.schemes import Scheme, SchemeRepository
from schemes.infrastructure.api.authorities import AuthorityModel
from schemes.infrastructure.api.base import BaseModel
from schemes.infrastructure.api.collections import CollectionModel
from schemes.infrastructure.api.dates import zoned_to_local
from schemes.infrastructure.api.funding_programmes import FundingProgrammeItemModel, FundingProgrammeModel
from schemes.infrastructure.api.observation_types import ObservationTypeModel
from schemes.infrastructure.api.schemes.overviews import CapitalSchemeOverviewModel
from schemes.oauth import AsyncBaseApp, ClientAsyncBaseApp


class BidStatusModel(str, Enum):
    SUBMITTED = "submitted"
    FUNDED = "funded"
    NOT_FUNDED = "not funded"
    SPLIT = "split"
    DELETED = "deleted"

    def to_domain(self) -> BidStatus:
        return BidStatus[self.name]


class CapitalSchemeBidStatusDetailsModel(BaseModel):
    bid_status: BidStatusModel

    def to_domain(self) -> BidStatusRevision:
        # TODO: id, effective
        return BidStatusRevision(
            id_=None, effective=DateRange(date_from=datetime.min, date_to=None), status=self.bid_status.to_domain()
        )


class FinancialTypeModel(str, Enum):
    EXPECTED_COST = "expected cost"
    ACTUAL_COST = "actual cost"
    FUNDING_ALLOCATION = "funding allocation"
    SPEND_TO_DATE = "spend to date"
    FUNDING_REQUEST = "funding request"

    def to_domain(self) -> FinancialType:
        return FinancialType[self.name]


class CapitalSchemeFinancialModel(BaseModel):
    type: FinancialTypeModel
    amount: int

    def to_domain(self) -> FinancialRevision:
        # TODO: id, effective, source
        return FinancialRevision(
            id_=None,
            effective=DateRange(date_from=datetime.min, date_to=None),
            type_=self.type.to_domain(),
            amount=self.amount,
            source=DataSource.PULSE_5,
        )


class MilestoneModel(str, Enum):
    PUBLIC_CONSULTATION_COMPLETED = "public consultation completed"
    FEASIBILITY_DESIGN_STARTED = "feasibility design started"
    FEASIBILITY_DESIGN_COMPLETED = "feasibility design completed"
    PRELIMINARY_DESIGN_COMPLETED = "preliminary design completed"
    OUTLINE_DESIGN_COMPLETED = "outline design completed"
    DETAILED_DESIGN_COMPLETED = "detailed design completed"
    CONSTRUCTION_STARTED = "construction started"
    CONSTRUCTION_COMPLETED = "construction completed"
    FUNDING_COMPLETED = "funding completed"
    NOT_PROGRESSED = "not progressed"
    SUPERSEDED = "superseded"
    REMOVED = "removed"

    def to_domain(self) -> Milestone:
        return Milestone[self.name]


class CapitalSchemeMilestoneModel(BaseModel):
    milestone: MilestoneModel
    observation_type: ObservationTypeModel
    status_date: date

    def to_domain(self) -> MilestoneRevision:
        # TODO: id, effective, source
        return MilestoneRevision(
            id_=None,
            effective=DateRange(date_from=datetime.min, date_to=None),
            milestone=self.milestone.to_domain(),
            observation_type=self.observation_type.to_domain(),
            status_date=self.status_date,
            source=DataSource.PULSE_5,
        )


class OutputTypeModel(str, Enum):
    NEW_SEGREGATED_CYCLING_FACILITY = "new segregated cycling facility"
    NEW_TEMPORARY_SEGREGATED_CYCLING_FACILITY = "new temporary segregated cycling facility"
    NEW_JUNCTION_TREATMENT = "new junction treatment"
    NEW_PERMANENT_FOOTWAY = "new permanent footway"
    NEW_TEMPORARY_FOOTWAY = "new temporary footway"
    NEW_SHARED_USE_WALKING_AND_CYCLING_FACILITIES = "new shared use (walking and cycling) facilities"
    NEW_SHARED_USE_WALKING_WHEELING_AND_CYCLING_FACILITIES = "new shared use (walking, wheeling & cycling) facilities"
    IMPROVEMENTS_TO_EXISTING_ROUTE = "improvements to make an existing walking/cycle route safer"
    AREA_WIDE_TRAFFIC_MANAGEMENT = "area-wide traffic management (including by TROs (both permanent and experimental))"
    BUS_PRIORITY_MEASURES = "bus priority measures that also enable active travel (for example, bus gates)"
    SECURE_CYCLE_PARKING = "provision of secure cycle parking facilities"
    NEW_ROAD_CROSSINGS = "new road crossings"
    RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY = "restriction or reduction of car parking availability"
    SCHOOL_STREETS = "school streets"
    UPGRADES_TO_EXISTING_FACILITIES = "upgrades to existing facilities (e.g. surfacing, signage, signals)"
    E_SCOOTER_TRIALS = "e-scooter trials"
    PARK_AND_CYCLE_STRIDE_FACILITIES = "park and cycle/stride facilities"
    TRAFFIC_CALMING = "traffic calming (e.g. lane closures, reducing speed limits)"
    WIDENING_EXISTING_FOOTWAY = "widening existing footway"
    OTHER_INTERVENTIONS = "other interventions"

    def to_domain(self) -> OutputType:
        return OutputType[self.name]


class OutputMeasureModel(str, Enum):
    MILES = "miles"
    NUMBER_OF_JUNCTIONS = "number of junctions"
    SIZE_OF_AREA = "size of area"
    NUMBER_OF_PARKING_SPACES = "number of parking spaces"
    NUMBER_OF_CROSSINGS = "number of crossings"
    NUMBER_OF_SCHOOL_STREETS = "number of school streets"
    NUMBER_OF_TRIALS = "number of trials"
    NUMBER_OF_BUS_GATES = "number of bus gates"
    NUMBER_OF_UPGRADES = "number of upgrades"
    NUMBER_OF_CHILDREN_AFFECTED = "number of children affected"
    NUMBER_OF_MEASURES_PLANNED = "number of measures planned"

    def to_domain(self) -> OutputMeasure:
        return OutputMeasure[self.name]


class CapitalSchemeOutputModel(BaseModel):
    type: OutputTypeModel
    measure: OutputMeasureModel
    observation_type: ObservationTypeModel
    value: Decimal

    def to_domain(self) -> OutputRevision:
        # TODO: id, effective
        return OutputRevision(
            id_=None,
            effective=DateRange(date_from=datetime.min, date_to=None),
            type_measure=OutputTypeMeasure.from_type_and_measure(self.type.to_domain(), self.measure.to_domain()),
            value=self.value,
            observation_type=self.observation_type.to_domain(),
        )


class CapitalSchemeAuthorityReviewModel(BaseModel):
    review_date: datetime

    def to_domain(self) -> AuthorityReview:
        # TODO: id, source
        return AuthorityReview(id_=None, review_date=zoned_to_local(self.review_date), source=DataSource.PULSE_5)


class CapitalSchemeModel(BaseModel):
    reference: str
    overview: CapitalSchemeOverviewModel
    bid_status_details: CapitalSchemeBidStatusDetailsModel
    financials: CollectionModel[CapitalSchemeFinancialModel]
    milestones: CollectionModel[CapitalSchemeMilestoneModel]
    outputs: CollectionModel[CapitalSchemeOutputModel]
    authority_review: CapitalSchemeAuthorityReviewModel | None = None

    def to_domain(
        self,
        authority_models: list[AuthorityModel],
        funding_programme_item_models: list[FundingProgrammeModel] | list[FundingProgrammeItemModel],
    ) -> Scheme:
        # TODO: id
        scheme = Scheme(id_=0, reference=self.reference)
        scheme.overview.update_overview(self.overview.to_domain(authority_models, funding_programme_item_models))
        scheme.funding.update_bid_status(self.bid_status_details.to_domain())
        scheme.funding.update_financials(*[financial.to_domain() for financial in self.financials.items])
        scheme.milestones.update_milestones(*[milestone.to_domain() for milestone in self.milestones.items])
        scheme.outputs.update_outputs(*[output.to_domain() for output in self.outputs.items])

        if self.authority_review:
            scheme.reviews.update_authority_review(self.authority_review.to_domain())

        return scheme


class ApiSchemeRepository(SchemeRepository):
    def __init__(self, remote_app: ClientAsyncBaseApp):
        self._remote_app = remote_app

    async def get(self, reference: str) -> Scheme | None:
        async with self._remote_app.client() as client:
            response = await client.get(f"/capital-schemes/{reference}", request=self._dummy_request())

            if response.status_code == 404:
                return None

            response.raise_for_status()
            capital_scheme_model = CapitalSchemeModel.model_validate(response.json())

            authority_url = capital_scheme_model.overview.bid_submitting_authority
            authority_models = [await self._get_authority_model_by_url(client, str(authority_url))]

            funding_programme_url = capital_scheme_model.overview.funding_programme
            funding_programme_models = [
                await self._get_funding_programme_model_by_url(client, str(funding_programme_url))
            ]

            return capital_scheme_model.to_domain(authority_models, funding_programme_models)

    async def get_by_authority(self, authority_abbreviation: str) -> list[Scheme]:
        async with self._remote_app.client() as client:
            authority_url = f"/authorities/{authority_abbreviation}"
            authority_model = await self._get_authority_model_by_url(client, authority_url)
            funding_programme_item_models = await self._get_funding_programme_item_models(client)
            funding_programme_codes = [
                funding_programme_item_model.code for funding_programme_item_model in funding_programme_item_models
            ]
            milestones = await self._get_milestones(client)

            collection_model = await self._get_capital_scheme_urls_by_url(
                client, str(authority_model.bid_submitting_capital_schemes), funding_programme_codes, milestones
            )
            capital_scheme_models = await asyncio.gather(
                *[
                    self._get_capital_scheme_model_by_url(client, str(capital_scheme_url))
                    for capital_scheme_url in collection_model.items
                ]
            )
            return [
                capital_scheme_model.to_domain([authority_model], funding_programme_item_models)
                for capital_scheme_model in capital_scheme_models
            ]

    async def _get_funding_programme_item_models(self, remote_app: AsyncBaseApp) -> list[FundingProgrammeItemModel]:
        response = await remote_app.get(
            "/funding-programmes", params={"eligible-for-authority-update": "true"}, request=self._dummy_request()
        )
        response.raise_for_status()
        return CollectionModel[FundingProgrammeItemModel].model_validate(response.json()).items

    async def _get_funding_programme_model_by_url(self, remote_app: AsyncBaseApp, url: str) -> FundingProgrammeModel:
        response = await remote_app.get(url, request=self._dummy_request())
        response.raise_for_status()
        return FundingProgrammeModel.model_validate(response.json())

    async def _get_milestones(self, remote_app: AsyncBaseApp) -> list[str]:
        response = await remote_app.get(
            "/capital-schemes/milestones", params={"active": "true", "complete": "false"}, request=self._dummy_request()
        )
        response.raise_for_status()

        collection_model = CollectionModel[str].model_validate(response.json())
        no_milestone = ""
        return collection_model.items + [no_milestone]

    async def _get_capital_scheme_urls_by_url(
        self,
        remote_app: AsyncBaseApp,
        url: str,
        funding_programme_codes: list[str],
        current_milestones: list[str],
    ) -> CollectionModel[AnyUrl]:
        response = await remote_app.get(
            url,
            params={
                "funding-programme-code": funding_programme_codes,
                "bid-status": "funded",
                "current-milestone": current_milestones,
            },
            request=self._dummy_request(),
        )
        response.raise_for_status()
        return CollectionModel[AnyUrl].model_validate(response.json())

    async def _get_capital_scheme_model_by_url(self, remote_app: AsyncBaseApp, url: str) -> CapitalSchemeModel:
        response = await remote_app.get(url, request=self._dummy_request())
        response.raise_for_status()
        return CapitalSchemeModel.model_validate(response.json())

    async def _get_authority_model_by_url(self, remote_app: AsyncBaseApp, url: str) -> AuthorityModel:
        response = await remote_app.get(url, request=self._dummy_request())
        response.raise_for_status()
        return AuthorityModel.model_validate(response.json())

    # See: https://github.com/authlib/authlib/issues/818#issuecomment-3257950062
    @staticmethod
    def _dummy_request() -> Any:
        return object()
