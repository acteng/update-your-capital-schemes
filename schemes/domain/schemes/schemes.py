from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto, unique

from schemes.domain.schemes.funding import BidStatus, SchemeFunding
from schemes.domain.schemes.milestones import Milestone, SchemeMilestones
from schemes.domain.schemes.outputs import SchemeOutputs
from schemes.domain.schemes.reviews import SchemeReviews


class Scheme:
    def __init__(self, id_: int, name: str, authority_id: int, type_: SchemeType):
        self.id = id_
        self.name = name
        self.authority_id = authority_id
        self.type = type_
        self.funding_programme: FundingProgramme | None = None
        self._funding = SchemeFunding()
        self._milestones = SchemeMilestones()
        self._outputs = SchemeOutputs()
        self._reviews = SchemeReviews()

    @property
    def reference(self) -> str:
        return f"ATE{self.id:05}"

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
        is_funded = self.funding.bid_status == BidStatus.FUNDED
        is_active_and_incomplete = self._is_active_and_incomplete(self.milestones.current_milestone)
        is_under_embargo = self.funding_programme and self.funding_programme.is_under_embargo
        return is_funded and is_active_and_incomplete and not is_under_embargo

    @staticmethod
    def _is_active_and_incomplete(milestone: Milestone | None) -> bool:
        return not milestone or (milestone.is_active and not milestone.is_complete)


@unique
class SchemeType(Enum):
    DEVELOPMENT = auto()
    CONSTRUCTION = auto()


@dataclass(frozen=True)
class FundingProgramme:
    code: str
    is_under_embargo: bool


class FundingProgrammes:
    ATF2 = FundingProgramme("ATF2", False)
    ATF3 = FundingProgramme("ATF3", False)
    ATF4 = FundingProgramme("ATF4", False)
    ATF4E = FundingProgramme("ATF4e", False)
    ATF5 = FundingProgramme("ATF5", False)
    MRN = FundingProgramme("MRN", False)
    LUF = FundingProgramme("LUF", False)
    CRSTS = FundingProgramme("CRSTS", False)


class SchemeRepository:
    def add(self, *schemes: Scheme) -> None:
        raise NotImplementedError()

    def clear(self) -> None:
        raise NotImplementedError()

    def get(self, id_: int) -> Scheme | None:
        raise NotImplementedError()

    def get_by_authority(self, authority_id: int) -> list[Scheme]:
        raise NotImplementedError()

    def update(self, scheme: Scheme) -> None:
        raise NotImplementedError()
