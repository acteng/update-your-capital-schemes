from typing import Annotated

from pydantic import AnyUrl, Field

from schemes.domain.schemes.overview import FundingProgramme
from schemes.infrastructure.api.base import BaseModel


class FundingProgrammeItemModel(BaseModel):
    id: Annotated[AnyUrl, Field(alias="@id")]
    code: str

    def to_domain(self) -> FundingProgramme:
        # TODO: is_under_embargo, is_eligible_for_authority_update
        return FundingProgramme(code=self.code, is_under_embargo=False, is_eligible_for_authority_update=True)
