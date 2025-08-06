from datetime import datetime
from typing import Annotated

from pydantic import AnyUrl, Field
from requests import Response

from schemes.domain.dates import DateRange
from schemes.domain.schemes.data_sources import DataSource
from schemes.domain.schemes.funding import BidStatus, BidStatusRevision
from schemes.domain.schemes.overview import FundingProgramme, OverviewRevision, SchemeType
from schemes.domain.schemes.reviews import AuthorityReview
from schemes.domain.schemes.schemes import Scheme, SchemeRepository
from schemes.infrastructure.api.base import BaseModel
from schemes.infrastructure.api.collections import CollectionModel
from schemes.infrastructure.api.dates import zoned_to_local
from schemes.infrastructure.api.oauth import RemoteApp


class ApiSchemeRepository(SchemeRepository):
    def __init__(self, remote_app: RemoteApp):
        self._remote_app = remote_app

    def get_by_authority(self, authority_abbreviation: str) -> list[Scheme]:
        funding_programmes = self._get_funding_programmes()

        response: Response = self._remote_app.get(
            f"/authorities/{authority_abbreviation}/capital-schemes/bid-submitting"
        )
        response.raise_for_status()

        collection_model = CollectionModel[AnyUrl].model_validate(response.json())
        return [
            self._get_by_url(str(capital_scheme_url), funding_programmes)
            for capital_scheme_url in collection_model.items
        ]

    def _get_funding_programmes(self) -> dict[str, FundingProgramme]:
        response: Response = self._remote_app.get("/funding-programmes")
        response.raise_for_status()

        collection_model = CollectionModel[FundingProgrammeItemModel].model_validate(response.json())
        return {
            str(funding_programme_item.id): funding_programme_item.to_domain()
            for funding_programme_item in collection_model.items
        }

    def _get_by_url(self, url: str, funding_programmes: dict[str, FundingProgramme]) -> Scheme:
        response: Response = self._remote_app.get(url)
        response.raise_for_status()

        capital_scheme_model = CapitalSchemeModel.model_validate(response.json())
        return capital_scheme_model.to_domain(funding_programmes)


class FundingProgrammeItemModel(BaseModel):
    id: Annotated[AnyUrl, Field(alias="@id")]
    code: str

    def to_domain(self) -> FundingProgramme:
        # TODO: is_under_embargo, is_eligible_for_authority_update
        return FundingProgramme(code=self.code, is_under_embargo=False, is_eligible_for_authority_update=True)


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


class CapitalSchemeAuthorityReviewModel(BaseModel):
    review_date: datetime

    def to_domain(self) -> AuthorityReview:
        # TODO: id, source
        return AuthorityReview(id_=None, review_date=zoned_to_local(self.review_date), source=DataSource.PULSE_5)


class CapitalSchemeModel(BaseModel):
    reference: str
    overview: CapitalSchemeOverviewModel
    authority_review: CapitalSchemeAuthorityReviewModel | None = None

    def to_domain(self, funding_programmes: dict[str, FundingProgramme]) -> Scheme:
        # TODO: id
        scheme = Scheme(id_=0, reference=self.reference)
        scheme.overview.update_overview(self.overview.to_domain(funding_programmes))
        # TODO: bid_status
        scheme.funding.update_bid_status(
            BidStatusRevision(
                id_=None, effective=DateRange(date_from=datetime.min, date_to=None), status=BidStatus.FUNDED
            )
        )

        if self.authority_review:
            scheme.reviews.update_authority_review(self.authority_review.to_domain())

        return scheme
