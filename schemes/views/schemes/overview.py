from __future__ import annotations

from datetime import datetime
from enum import Enum, unique
from typing import Self

from pydantic import BaseModel

from schemes.dicts import inverse_dict
from schemes.domain.dates import DateRange
from schemes.domain.schemes.overview import FundingProgramme, FundingProgrammes, OverviewRevision, SchemeType


@unique
class SchemeTypeRepr(str, Enum):
    DEVELOPMENT = "development"
    CONSTRUCTION = "construction"

    @classmethod
    def from_domain(cls, type_: SchemeType) -> SchemeTypeRepr:
        return cls._members()[type_]

    def to_domain(self) -> SchemeType:
        return inverse_dict(self._members())[self]

    @staticmethod
    def _members() -> dict[SchemeType, SchemeTypeRepr]:
        return {
            SchemeType.DEVELOPMENT: SchemeTypeRepr.DEVELOPMENT,
            SchemeType.CONSTRUCTION: SchemeTypeRepr.CONSTRUCTION,
        }


@unique
class FundingProgrammeRepr(str, Enum):
    ATF2 = "ATF2"
    ATF3 = "ATF3"
    ATF4 = "ATF4"
    ATF4E = "ATF4e"
    ATF5 = "ATF5"
    CATF = "CATF"
    CRSTS = "CRSTS"
    IST = "IST"
    LUF1 = "LUF1"
    LUF2 = "LUF2"
    LUF3 = "LUF3"
    MRN = "MRN"

    @classmethod
    def from_domain(cls, funding_programme: FundingProgramme) -> FundingProgrammeRepr:
        return cls._members()[funding_programme]

    def to_domain(self) -> FundingProgramme:
        return inverse_dict(self._members())[self]

    @staticmethod
    def _members() -> dict[FundingProgramme, FundingProgrammeRepr]:
        return {
            FundingProgrammes.ATF2: FundingProgrammeRepr.ATF2,
            FundingProgrammes.ATF3: FundingProgrammeRepr.ATF3,
            FundingProgrammes.ATF4: FundingProgrammeRepr.ATF4,
            FundingProgrammes.ATF4E: FundingProgrammeRepr.ATF4E,
            FundingProgrammes.ATF5: FundingProgrammeRepr.ATF5,
            FundingProgrammes.CATF: FundingProgrammeRepr.CATF,
            FundingProgrammes.CRSTS: FundingProgrammeRepr.CRSTS,
            FundingProgrammes.IST: FundingProgrammeRepr.IST,
            FundingProgrammes.LUF1: FundingProgrammeRepr.LUF1,
            FundingProgrammes.LUF2: FundingProgrammeRepr.LUF2,
            FundingProgrammes.LUF3: FundingProgrammeRepr.LUF3,
            FundingProgrammes.MRN: FundingProgrammeRepr.MRN,
        }


class OverviewRevisionRepr(BaseModel):
    name: str
    authority_abbreviation: str
    type: SchemeTypeRepr
    funding_programme: FundingProgrammeRepr
    effective_date_from: str
    effective_date_to: str | None
    id: int | None = None

    @classmethod
    def from_domain(cls, overview_revision: OverviewRevision) -> Self:
        return cls(
            id=overview_revision.id,
            effective_date_from=overview_revision.effective.date_from.isoformat(),
            effective_date_to=(
                overview_revision.effective.date_to.isoformat() if overview_revision.effective.date_to else None
            ),
            name=overview_revision.name,
            authority_abbreviation=overview_revision.authority_abbreviation,
            type=SchemeTypeRepr.from_domain(overview_revision.type),
            funding_programme=FundingProgrammeRepr.from_domain(overview_revision.funding_programme),
        )

    def to_domain(self) -> OverviewRevision:
        return OverviewRevision(
            id_=self.id,
            effective=DateRange(
                date_from=datetime.fromisoformat(self.effective_date_from),
                date_to=datetime.fromisoformat(self.effective_date_to) if self.effective_date_to else None,
            ),
            name=self.name,
            authority_abbreviation=self.authority_abbreviation,
            type_=self.type.to_domain(),
            funding_programme=self.funding_programme.to_domain(),
        )
