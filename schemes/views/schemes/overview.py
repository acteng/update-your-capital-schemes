from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum, unique

from schemes.dicts import inverse_dict
from schemes.domain.dates import DateRange
from schemes.domain.schemes import OverviewRevision, SchemeType


@dataclass(frozen=True)
class OverviewRevisionRepr:
    name: str
    authority_id: int
    type: SchemeTypeRepr
    effective_date_from: str
    effective_date_to: str | None
    id: int | None = None

    @classmethod
    def from_domain(cls, overview_revision: OverviewRevision) -> OverviewRevisionRepr:
        return OverviewRevisionRepr(
            id=overview_revision.id,
            effective_date_from=overview_revision.effective.date_from.isoformat(),
            effective_date_to=(
                overview_revision.effective.date_to.isoformat() if overview_revision.effective.date_to else None
            ),
            name=overview_revision.name,
            authority_id=overview_revision.authority_id,
            type=SchemeTypeRepr.from_domain(overview_revision.type),
        )

    def to_domain(self) -> OverviewRevision:
        return OverviewRevision(
            id_=self.id,
            effective=DateRange(
                date_from=datetime.fromisoformat(self.effective_date_from),
                date_to=datetime.fromisoformat(self.effective_date_to) if self.effective_date_to else None,
            ),
            name=self.name,
            authority_id=self.authority_id,
            type_=self.type.to_domain(),
        )


@unique
class SchemeTypeRepr(Enum):
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
