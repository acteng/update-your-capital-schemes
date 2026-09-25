from pydantic import AnyUrl

from schemes.infrastructure.api.base import BaseModel
from schemes.infrastructure.api.data_sources import DataSourceModel


class ImprovementOverviewModel(BaseModel):
    name: str
    description: str | None = None
    funding_managed_by: AnyUrl
    source: DataSourceModel


class ImprovementModel(BaseModel):
    reference: str
    overview: ImprovementOverviewModel
