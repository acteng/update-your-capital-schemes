from __future__ import annotations

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
    def authority_id(self) -> int | None:
        current_overview_revision = self._current_overview_revision()
        return current_overview_revision.authority_id if current_overview_revision else None

    def _current_overview_revision(self) -> OverviewRevision | None:
        return next((overview for overview in self.overview_revisions if overview.effective.date_to is None), None)


class OverviewRevision:
    # TODO: domain identifier should be mandatory for transient instances
    def __init__(self, id_: int | None, effective: DateRange, authority_id: int):
        self.id = id_
        self.effective = effective
        self.authority_id = authority_id
