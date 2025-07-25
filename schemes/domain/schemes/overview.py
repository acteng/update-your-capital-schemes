from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto, unique

from schemes.domain.dates import DateRange


class SchemeOverview:
    def __init__(self) -> None:
        self._overview_revisions: list[OverviewRevision] = []

    @property
    def overview_revisions(self) -> list[OverviewRevision]:
        return list(self._overview_revisions)

    def update_overview(self, overview_revision: OverviewRevision) -> None:
        self._overview_revisions.append(overview_revision)

    def update_overviews(self, *overview_revisions: OverviewRevision) -> None:
        for overview_revision in overview_revisions:
            self.update_overview(overview_revision)

    @property
    def name(self) -> str | None:
        current_overview_revision = self._current_overview_revision()
        return current_overview_revision.name if current_overview_revision else None

    @property
    def authority_abbreviation(self) -> str | None:
        current_overview_revision = self._current_overview_revision()
        return current_overview_revision.authority_abbreviation if current_overview_revision else None

    @property
    def type(self) -> SchemeType | None:
        current_overview_revision = self._current_overview_revision()
        return current_overview_revision.type if current_overview_revision else None

    @property
    def funding_programme(self) -> FundingProgramme | None:
        current_overview_revision = self._current_overview_revision()
        return current_overview_revision.funding_programme if current_overview_revision else None

    def _current_overview_revision(self) -> OverviewRevision | None:
        return next((overview for overview in self.overview_revisions if overview.effective.date_to is None), None)


class OverviewRevision:
    # TODO: domain identifier should be mandatory for transient instances
    def __init__(
        self,
        id_: int | None,
        effective: DateRange,
        name: str,
        authority_abbreviation: str,
        type_: SchemeType,
        funding_programme: FundingProgramme,
    ):
        self._id = id_
        self._effective = effective
        self._name = name
        self._authority_abbreviation = authority_abbreviation
        self._type = type_
        self._funding_programme = funding_programme

    @property
    def id(self) -> int | None:
        return self._id

    @property
    def effective(self) -> DateRange:
        return self._effective

    @property
    def name(self) -> str:
        return self._name

    @property
    def authority_abbreviation(self) -> str:
        return self._authority_abbreviation

    @property
    def type(self) -> SchemeType:
        return self._type

    @property
    def funding_programme(self) -> FundingProgramme:
        return self._funding_programme


@unique
class SchemeType(Enum):
    DEVELOPMENT = auto()
    CONSTRUCTION = auto()


@dataclass(frozen=True)
class FundingProgramme:
    code: str
    is_under_embargo: bool
    is_eligible_for_authority_update: bool


class FundingProgrammes:
    ATF2 = FundingProgramme("ATF2", False, True)
    ATF3 = FundingProgramme("ATF3", False, True)
    ATF4 = FundingProgramme("ATF4", False, True)
    ATF4E = FundingProgramme("ATF4e", False, True)
    ATF5 = FundingProgramme("ATF5", False, True)
    CATF = FundingProgramme("CATF", False, True)
    CRSTS = FundingProgramme("CRSTS", False, False)
    LUF1 = FundingProgramme("LUF1", False, False)
    LUF2 = FundingProgramme("LUF2", False, False)
    LUF3 = FundingProgramme("LUF3", False, False)
    MRN = FundingProgramme("MRN", False, False)
