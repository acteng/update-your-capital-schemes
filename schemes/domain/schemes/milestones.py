from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum, IntEnum, auto

from schemes.domain.schemes.dates import DateRange


@dataclass(frozen=True)
class MilestoneRevision:
    effective: DateRange
    milestone: Milestone
    observation_type: ObservationType
    status_date: date


class Milestone(IntEnum):
    PUBLIC_CONSULTATION_COMPLETED = auto()
    FEASIBILITY_DESIGN_COMPLETED = auto()
    PRELIMINARY_DESIGN_COMPLETED = auto()
    OUTLINE_DESIGN_COMPLETED = auto()
    DETAILED_DESIGN_COMPLETED = auto()
    CONSTRUCTION_STARTED = auto()
    CONSTRUCTION_COMPLETED = auto()
    INSPECTION = auto()
    NOT_PROGRESSED = auto()
    SUPERSEDED = auto()
    REMOVED = auto()


class ObservationType(Enum):
    PLANNED = auto()
    ACTUAL = auto()
