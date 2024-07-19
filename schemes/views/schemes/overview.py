from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from schemes.domain.dates import DateRange
from schemes.domain.schemes import OverviewRevision


@dataclass(frozen=True)
class OverviewRevisionRepr:
    authority_id: int
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
            authority_id=overview_revision.authority_id,
        )

    def to_domain(self) -> OverviewRevision:
        return OverviewRevision(
            id_=self.id,
            effective=DateRange(
                date_from=datetime.fromisoformat(self.effective_date_from),
                date_to=datetime.fromisoformat(self.effective_date_to) if self.effective_date_to else None,
            ),
            authority_id=self.authority_id,
        )
