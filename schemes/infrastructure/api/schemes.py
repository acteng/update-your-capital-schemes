import asyncio
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import AnyUrl

from schemes.domain.dates import DateRange
from schemes.domain.schemes.data_sources import DataSource
from schemes.domain.schemes.funding import BidStatus, BidStatusRevision, FinancialRevision, FinancialType
from schemes.domain.schemes.overview import OverviewRevision, SchemeType
from schemes.domain.schemes.reviews import AuthorityReview
from schemes.domain.schemes.schemes import Scheme, SchemeRepository
from schemes.infrastructure.api.authorities import AuthorityModel
from schemes.infrastructure.api.base import BaseModel
from schemes.infrastructure.api.collections import CollectionModel
from schemes.infrastructure.api.dates import zoned_to_local
from schemes.infrastructure.api.funding_programmes import FundingProgrammeItemModel, FundingProgrammeModel
from schemes.oauth import AsyncBaseApp, ClientAsyncBaseApp


class CapitalSchemeTypeModel(str, Enum):
    DEVELOPMENT = "development"
    CONSTRUCTION = "construction"

    def to_domain(self) -> SchemeType:
        return SchemeType[self.name]


class CapitalSchemeOverviewModel(BaseModel):
    name: str
    bid_submitting_authority: AnyUrl
    funding_programme: AnyUrl
    type: CapitalSchemeTypeModel

    def to_domain(
        self,
        authority_models: list[AuthorityModel],
        funding_programme_item_models: list[FundingProgrammeModel] | list[FundingProgrammeItemModel],
    ) -> OverviewRevision:
        # TODO: id, effective, type
        return OverviewRevision(
            id_=None,
            effective=DateRange(date_from=datetime.min, date_to=None),
            name=self.name,
            authority_abbreviation=next(
                authority_model.abbreviation
                for authority_model in authority_models
                if authority_model.id == self.bid_submitting_authority
            ),
            type_=self.type.to_domain(),
            funding_programme=next(
                funding_programme_item_model.to_domain()
                for funding_programme_item_model in funding_programme_item_models
                if funding_programme_item_model.id == self.funding_programme
            ),
        )


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
