from pydantic import AnyUrl

from schemes.domain.schemes.overview import SchemeOverview
from schemes.infrastructure.api.authorities import AuthorityModel
from schemes.infrastructure.api.base import BaseModel


class CapitalSchemeOverviewModel(BaseModel):
    name: str
    improvement: AnyUrl | None = None

    def to_domain(self, authority_model: AuthorityModel) -> SchemeOverview:
        return SchemeOverview(name=self.name, authority_abbreviation=authority_model.abbreviation)
