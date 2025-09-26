import asyncio
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import AnyUrl

from schemes.domain.dates import DateRange
from schemes.domain.schemes.data_sources import DataSource
from schemes.domain.schemes.funding import BidStatus, BidStatusRevision
from schemes.domain.schemes.overview import FundingProgramme, OverviewRevision, SchemeType
from schemes.domain.schemes.reviews import AuthorityReview
from schemes.domain.schemes.schemes import Scheme, SchemeRepository
from schemes.infrastructure.api.base import BaseModel
from schemes.infrastructure.api.collections import CollectionModel
from schemes.infrastructure.api.dates import zoned_to_local
from schemes.infrastructure.api.funding_programmes import FundingProgrammeItemModel
from schemes.oauth import AsyncBaseApp, ClientAsyncBaseApp


class ApiSchemeRepository(SchemeRepository):
    def __init__(self, remote_app: ClientAsyncBaseApp):
        self._remote_app = remote_app

    async def get_by_authority(self, authority_abbreviation: str) -> list[Scheme]:
        async with self._remote_app.client() as client:
            funding_programmes = await self._get_funding_programmes(client)
            milestones = await self._get_milestones(client)

            response = await client.get(
                f"/authorities/{authority_abbreviation}/capital-schemes/bid-submitting",
                params={
                    "funding-programme-code": [
                        funding_programme.code for funding_programme in funding_programmes.values()
                    ],
                    "bid-status": "funded",
                    "current-milestone": milestones,
                },
                request=self._dummy_request(),
            )
            response.raise_for_status()

            collection_model = CollectionModel[AnyUrl].model_validate(response.json())
            return await asyncio.gather(
                *[
                    self._get_by_url(client, str(capital_scheme_url), funding_programmes)
                    for capital_scheme_url in collection_model.items
                ]
            )

    async def _get_funding_programmes(self, remote_app: AsyncBaseApp) -> dict[str, FundingProgramme]:
        response = await remote_app.get(
            "/funding-programmes", params={"eligible-for-authority-update": "true"}, request=self._dummy_request()
        )
        response.raise_for_status()

        collection_model = CollectionModel[FundingProgrammeItemModel].model_validate(response.json())
        return {
            str(funding_programme_item_model.id): funding_programme_item_model.to_domain()
            for funding_programme_item_model in collection_model.items
        }

    async def _get_milestones(self, remote_app: AsyncBaseApp) -> list[str]:
        response = await remote_app.get(
            "/capital-schemes/milestones", params={"active": "true", "complete": "false"}, request=self._dummy_request()
        )
        response.raise_for_status()

        collection_model = CollectionModel[str].model_validate(response.json())
        no_milestone = ""
        return collection_model.items + [no_milestone]

    async def _get_by_url(
        self, remote_app: AsyncBaseApp, url: str, funding_programmes: dict[str, FundingProgramme]
    ) -> Scheme:
        response = await remote_app.get(url, request=self._dummy_request())
        response.raise_for_status()

        capital_scheme_model = CapitalSchemeModel.model_validate(response.json())
        return capital_scheme_model.to_domain(funding_programmes)

    # See: https://github.com/authlib/authlib/issues/818#issuecomment-3257950062
    @staticmethod
    def _dummy_request() -> Any:
        return object()


class CapitalSchemeOverviewModel(BaseModel):
    name: str
    funding_programme: AnyUrl

    def to_domain(self, funding_programmes: dict[str, FundingProgramme]) -> OverviewRevision:
        # TODO: id, effective, authority_abbreviation, type
        return OverviewRevision(
            id_=None,
            effective=DateRange(date_from=datetime.min, date_to=None),
            name=self.name,
            authority_abbreviation="",
            type_=SchemeType.DEVELOPMENT,
            funding_programme=funding_programmes[str(self.funding_programme)],
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


class CapitalSchemeAuthorityReviewModel(BaseModel):
    review_date: datetime

    def to_domain(self) -> AuthorityReview:
        # TODO: id, source
        return AuthorityReview(id_=None, review_date=zoned_to_local(self.review_date), source=DataSource.PULSE_5)


class CapitalSchemeModel(BaseModel):
    reference: str
    overview: CapitalSchemeOverviewModel
    bid_status_details: CapitalSchemeBidStatusDetailsModel
    authority_review: CapitalSchemeAuthorityReviewModel | None = None

    def to_domain(self, funding_programmes: dict[str, FundingProgramme]) -> Scheme:
        # TODO: id
        scheme = Scheme(id_=0, reference=self.reference)
        scheme.overview.update_overview(self.overview.to_domain(funding_programmes))
        scheme.funding.update_bid_status(self.bid_status_details.to_domain())

        if self.authority_review:
            scheme.reviews.update_authority_review(self.authority_review.to_domain())

        return scheme
