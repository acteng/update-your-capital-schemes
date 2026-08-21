from enum import Enum, auto

from schemes.domain.schemes.funding import SchemeFunding
from schemes.domain.schemes.milestones import Milestone, SchemeMilestones
from schemes.domain.schemes.outputs import SchemeOutputs
from schemes.domain.schemes.overview import FundingProgramme, SchemeOverview, SchemeType
from schemes.domain.schemes.reviews import SchemeReviews


class Status(Enum):
    PIPELINE = auto()
    ACTIVE = auto()
    PAUSED = auto()
    CONCLUDED = auto()
    DELETED = auto()


class Scheme:
    def __init__(self, reference: str, status: Status):
        self._reference = reference
        self._status = status
        self._overview = SchemeOverview()
        self._funding = SchemeFunding()
        self._milestones = SchemeMilestones()
        self._outputs = SchemeOutputs()
        self._reviews = SchemeReviews()

    @property
    def reference(self) -> str:
        return self._reference

    @property
    def status(self) -> Status:
        return self._status

    @property
    def overview(self) -> SchemeOverview:
        return self._overview

    @property
    def funding(self) -> SchemeFunding:
        return self._funding

    @property
    def milestones(self) -> SchemeMilestones:
        return self._milestones

    @property
    def outputs(self) -> SchemeOutputs:
        return self._outputs

    @property
    def reviews(self) -> SchemeReviews:
        return self._reviews

    @property
    def is_updateable(self) -> bool:
        is_active = self.status == Status.ACTIVE
        is_eligible_for_authority_update = self._is_eligible_for_authority_update(self.overview.funding_programme)
        return is_active and is_eligible_for_authority_update

    @staticmethod
    def _is_eligible_for_authority_update(funding_programme: FundingProgramme | None) -> bool:
        return funding_programme.is_eligible_for_authority_update if funding_programme else True

    @property
    def milestones_eligible_for_authority_update(self) -> set[Milestone]:
        milestones = {
            Milestone.FEASIBILITY_DESIGN_COMPLETED,
            Milestone.PRELIMINARY_DESIGN_COMPLETED,
            Milestone.DETAILED_DESIGN_COMPLETED,
        }
        if self.overview.type == SchemeType.CONSTRUCTION:
            milestones = milestones | {Milestone.CONSTRUCTION_STARTED, Milestone.CONSTRUCTION_COMPLETED}
        return milestones


class SchemeRepository:
    async def add(self, *schemes: Scheme) -> None:
        raise NotImplementedError()

    async def clear(self) -> None:
        raise NotImplementedError()

    async def get(self, reference: str) -> Scheme | None:
        raise NotImplementedError()

    async def get_by_authority(self, authority_abbreviation: str) -> list[Scheme]:
        raise NotImplementedError()

    async def update(self, scheme: Scheme) -> None:
        raise NotImplementedError()
