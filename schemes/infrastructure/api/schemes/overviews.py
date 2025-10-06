from datetime import datetime
from enum import Enum

from pydantic import AnyUrl

from schemes.domain.dates import DateRange
from schemes.domain.schemes.overview import OverviewRevision, SchemeType
from schemes.infrastructure.api.authorities import AuthorityModel
from schemes.infrastructure.api.base import BaseModel
from schemes.infrastructure.api.funding_programmes import FundingProgrammeItemModel, FundingProgrammeModel


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
