from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum, IntEnum, auto

from schemes.domain.schemes.dates import DateRange
from schemes.domain.schemes.funding import DataSource, FinancialRevision, FinancialType


class Scheme:
    def __init__(self, id_: int, name: str, authority_id: int):
        self.id = id_
        self.name = name
        self.authority_id = authority_id
        self.type: SchemeType | None = None
        self.funding_programme: FundingProgramme | None = None
        self._milestone_revisions: list[MilestoneRevision] = []
        self._financial_revisions: list[FinancialRevision] = []

    @property
    def reference(self) -> str:
        return f"ATE{self.id:05}"

    @property
    def milestone_revisions(self) -> list[MilestoneRevision]:
        return list(self._milestone_revisions)

    @property
    def current_milestone_revisions(self) -> list[MilestoneRevision]:
        return [revision for revision in self._milestone_revisions if revision.effective.date_to is None]

    def update_milestone(self, milestone_revision: MilestoneRevision) -> None:
        self._milestone_revisions.append(milestone_revision)

    def update_milestones(self, *milestone_revisions: MilestoneRevision) -> None:
        for milestone_revision in milestone_revisions:
            self.update_milestone(milestone_revision)

    @property
    def current_milestone(self) -> Milestone | None:
        actual_milestones = [
            revision.milestone
            for revision in self.current_milestone_revisions
            if revision.observation_type == ObservationType.ACTUAL
        ]
        return sorted(actual_milestones)[-1] if actual_milestones else None

    @property
    def financial_revisions(self) -> list[FinancialRevision]:
        return list(self._financial_revisions)

    def update_financial(self, financial_revision: FinancialRevision) -> None:
        if financial_revision.is_current_funding_allocation:
            self._ensure_no_current_funding_allocation()

        if financial_revision.is_current_spent_to_date:
            self._ensure_no_current_spent_to_date()

        self._financial_revisions.append(financial_revision)

    def update_financials(self, *financial_revisions: FinancialRevision) -> None:
        for financial_revision in financial_revisions:
            self.update_financial(financial_revision)

    def _ensure_no_current_funding_allocation(self) -> None:
        current_funding_allocation = next(
            (revision for revision in self._financial_revisions if revision.is_current_funding_allocation), None
        )
        if current_funding_allocation:
            raise ValueError(f"Current funding allocation already exists: {current_funding_allocation}")

    def _ensure_no_current_spent_to_date(self) -> None:
        current_spent_to_date = next(
            (revision for revision in self._financial_revisions if revision.is_current_spent_to_date), None
        )
        if current_spent_to_date:
            raise ValueError(f"Current spent to date already exists: {current_spent_to_date}")

    @property
    def funding_allocation(self) -> Decimal | None:
        amounts = (revision.amount for revision in self._financial_revisions if revision.is_current_funding_allocation)
        return next(amounts, None)

    @property
    def spend_to_date(self) -> Decimal | None:
        amounts = (revision.amount for revision in self._financial_revisions if revision.is_current_spent_to_date)
        return next(amounts, None)

    @property
    def change_control_adjustment(self) -> Decimal | None:
        amounts = [
            revision.amount
            for revision in self._financial_revisions
            if revision.type == FinancialType.FUNDING_ALLOCATION
            and revision.source == DataSource.CHANGE_CONTROL
            and revision.effective.date_to is None
        ]
        return sum(amounts, Decimal(0)) if amounts else None

    @property
    def allocation_still_to_spend(self) -> Decimal:
        funding_allocation = self.funding_allocation or Decimal(0)
        spend_to_date = self.spend_to_date or Decimal(0)
        change_control_adjustment = self.change_control_adjustment or Decimal(0)
        return funding_allocation + change_control_adjustment - spend_to_date


class SchemeType(Enum):
    DEVELOPMENT = auto()
    CONSTRUCTION = auto()


class FundingProgramme(Enum):
    ATF2 = auto()
    ATF3 = auto()
    ATF4 = auto()
    ATF4E = auto()
    ATF5 = auto()
    MRN = auto()
    LUF = auto()
    CRSTS = auto()


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


class SchemeRepository:
    def add(self, *schemes: Scheme) -> None:
        raise NotImplementedError()

    def clear(self) -> None:
        raise NotImplementedError()

    def get(self, id_: int) -> Scheme | None:
        raise NotImplementedError()

    def get_by_authority(self, authority_id: int) -> list[Scheme]:
        raise NotImplementedError()
