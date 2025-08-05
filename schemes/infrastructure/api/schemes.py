from datetime import datetime

from pydantic import AnyUrl
from requests import Response

from schemes.domain.dates import DateRange
from schemes.domain.schemes.funding import BidStatus, BidStatusRevision
from schemes.domain.schemes.overview import FundingProgrammes, OverviewRevision, SchemeType
from schemes.domain.schemes.schemes import Scheme, SchemeRepository
from schemes.infrastructure.api.base import BaseModel
from schemes.infrastructure.api.collections import CollectionModel
from schemes.infrastructure.api.oauth import RemoteApp


class ApiSchemeRepository(SchemeRepository):
    def __init__(self, remote_app: RemoteApp):
        self._remote_app = remote_app

    def get_by_authority(self, authority_abbreviation: str) -> list[Scheme]:
        response: Response = self._remote_app.get(
            f"/authorities/{authority_abbreviation}/capital-schemes/bid-submitting"
        )
        response.raise_for_status()

        collection_model = CollectionModel[AnyUrl].model_validate(response.json())
        return [self._get_by_url(str(capital_scheme_url)) for capital_scheme_url in collection_model.items]

    def _get_by_url(self, url: str) -> Scheme:
        response: Response = self._remote_app.get(url)
        response.raise_for_status()

        capital_scheme_model = CapitalSchemeModel.model_validate(response.json())
        return capital_scheme_model.to_domain()


class CapitalSchemeOverviewModel(BaseModel):
    name: str

    def to_domain(self) -> OverviewRevision:
        # TODO: id, effective, authority_abbreviation, type, funding_programme
        return OverviewRevision(
            id_=None,
            effective=DateRange(date_from=datetime.min, date_to=None),
            name=self.name,
            authority_abbreviation="",
            type_=SchemeType.DEVELOPMENT,
            funding_programme=FundingProgrammes.ATF2,
        )


class CapitalSchemeModel(BaseModel):
    reference: str
    overview: CapitalSchemeOverviewModel

    def to_domain(self) -> Scheme:
        # TODO: id
        scheme = Scheme(id_=0, reference=self.reference)
        scheme.overview.update_overview(self.overview.to_domain())
        # TODO: bid_status
        scheme.funding.update_bid_status(
            BidStatusRevision(
                id_=None, effective=DateRange(date_from=datetime.min, date_to=None), status=BidStatus.FUNDED
            )
        )

        return scheme
