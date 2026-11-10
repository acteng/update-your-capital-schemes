from enum import Enum, auto

from schemes.domain.schemes.financials import SchemeFinancials
from schemes.domain.schemes.milestones import SchemeMilestones
from schemes.domain.schemes.outputs import SchemeOutputs
from schemes.domain.schemes.overview import SchemeOverview
from schemes.domain.schemes.reviews import SchemeReviews


class Status(Enum):
    PIPELINE = auto()
    ACTIVE = auto()
    PAUSED = auto()
    CONCLUDED = auto()
    DELETED = auto()


class Scheme:
    def __init__(self, reference: str, overview: SchemeOverview, status: Status):
        self._reference = reference
        self._status = status
        self._overview = overview
        self._financials = SchemeFinancials()
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
    def financials(self) -> SchemeFinancials:
        return self._financials

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
        is_eligible_for_authority_update = any(
            funding.funding_programme.is_eligible_for_authority_update for funding in self.financials.fundings
        )
        return is_active and is_eligible_for_authority_update


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
