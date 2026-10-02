from datetime import datetime

from pydantic import AnyUrl

from schemes.domain.dates import DateRange
from schemes.domain.schemes.overview import OverviewRevision
from schemes.infrastructure.api.authorities import AuthorityModel
from schemes.infrastructure.api.base import BaseModel
from schemes.infrastructure.api.funding_programmes import FundingProgrammeItemModel, FundingProgrammeModel


class CapitalSchemeOverviewModel(BaseModel):
    name: str
    funding_programme: AnyUrl
    improvement: AnyUrl | None = None

    def to_domain(
        self,
        authority_model: AuthorityModel,
        funding_programme_item_models: list[FundingProgrammeModel] | list[FundingProgrammeItemModel],
    ) -> OverviewRevision:
        # TODO: effective
        return OverviewRevision(
            effective=DateRange(date_from=datetime.min, date_to=None),
            name=self.name,
            authority_abbreviation=authority_model.abbreviation,
            funding_programme=next(
                funding_programme_item_model.to_domain()
                for funding_programme_item_model in funding_programme_item_models
                if funding_programme_item_model.id == self.funding_programme
            ),
        )
