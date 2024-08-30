from __future__ import annotations

from schemes.domain.schemes.funding import BidStatus, SchemeFunding
from schemes.domain.schemes.milestones import Milestone, SchemeMilestones
from schemes.domain.schemes.outputs import SchemeOutputs
from schemes.domain.schemes.overview import FundingProgramme, SchemeOverview
from schemes.domain.schemes.reviews import SchemeReviews


class Scheme:
    def __init__(self, id_: int, reference: str):
        self.id = id_
        self._reference = reference
        self._overview = SchemeOverview()
        self._funding = SchemeFunding()
        self._milestones = SchemeMilestones()
        self._outputs = SchemeOutputs()
        self._reviews = SchemeReviews()

    @property
    def reference(self) -> str:
        return self._reference

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
        is_funded = self.funding.bid_status == BidStatus.FUNDED
        is_active_and_incomplete = self._is_active_and_incomplete(self.milestones.current_milestone)
        is_under_embargo = self._is_under_embargo(self.overview.funding_programme)
        is_eligible_for_authority_update = self._is_eligible_for_authority_update(self.overview.funding_programme)
        return is_funded and is_active_and_incomplete and not is_under_embargo and is_eligible_for_authority_update

    @staticmethod
    def _is_active_and_incomplete(milestone: Milestone | None) -> bool:
        return not milestone or (milestone.is_active and not milestone.is_complete)

    @staticmethod
    def _is_under_embargo(funding_programme: FundingProgramme | None) -> bool:
        return funding_programme.is_under_embargo if funding_programme else False

    @staticmethod
    def _is_eligible_for_authority_update(funding_programme: FundingProgramme | None) -> bool:
        return funding_programme.is_eligible_for_authority_update if funding_programme else True


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
