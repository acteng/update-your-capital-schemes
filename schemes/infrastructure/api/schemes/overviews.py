from pydantic import AnyUrl

from schemes.domain.schemes.overview import SchemeOverview
from schemes.infrastructure.api.authorities import AuthorityModel
from schemes.infrastructure.api.base import BaseModel
from schemes.infrastructure.api.funding_programmes import FundingProgrammeModel


class CapitalSchemeOverviewModel(BaseModel):
    name: str
    funding_programme: AnyUrl
    improvement: AnyUrl | None = None

    def to_domain(
        self,
        authority_model: AuthorityModel,
        funding_programme_models: list[FundingProgrammeModel],
    ) -> SchemeOverview:
        return SchemeOverview(
            name=self.name,
            authority_abbreviation=authority_model.abbreviation,
            funding_programme=next(
                funding_programme_model.to_domain()
                for funding_programme_model in funding_programme_models
                if funding_programme_model.id == self.funding_programme
            ),
        )
