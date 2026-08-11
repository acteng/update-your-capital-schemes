from enum import Enum

from schemes.domain.schemes.schemes import Status
from schemes.infrastructure.api.base import BaseModel


class StatusModel(str, Enum):
    PIPELINE = "pipeline"
    ACTIVE = "active"
    PAUSED = "paused"
    CONCLUDED = "concluded"
    DELETED = "deleted"

    def to_domain(self) -> Status:
        return Status[self.name]


class CapitalSchemeStatusModel(BaseModel):
    status: StatusModel
