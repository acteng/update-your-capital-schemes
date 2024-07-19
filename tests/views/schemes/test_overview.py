from datetime import datetime

from schemes.domain.dates import DateRange
from schemes.domain.schemes import OverviewRevision
from schemes.views.schemes.overview import OverviewRevisionRepr


class TestOverviewRevisionRepr:
    def test_from_domain(self) -> None:
        overview_revision = OverviewRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1, 12), datetime(2020, 2, 1, 13)),
            authority_id=2,
        )

        overview_revision_repr = OverviewRevisionRepr.from_domain(overview_revision)

        assert overview_revision_repr == OverviewRevisionRepr(
            id=1,
            effective_date_from="2020-01-01T12:00:00",
            effective_date_to="2020-02-01T13:00:00",
            authority_id=2,
        )

    def test_from_domain_when_no_effective_date_to(self) -> None:
        overview_revision = OverviewRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1), None),
            authority_id=2,
        )

        overview_revision_repr = OverviewRevisionRepr.from_domain(overview_revision)

        assert overview_revision_repr.effective_date_to is None

    def test_to_domain(self) -> None:
        overview_revision_repr = OverviewRevisionRepr(
            id=1,
            effective_date_from="2020-01-01T12:00:00",
            effective_date_to="2020-02-01T13:00:00",
            authority_id=2,
        )

        overview_revision = overview_revision_repr.to_domain()

        assert (
            overview_revision.id == 1
            and overview_revision.effective == DateRange(datetime(2020, 1, 1, 12), datetime(2020, 2, 1, 13))
            and overview_revision.authority_id == 2
        )

    def test_to_domain_when_no_effective_date_to(self) -> None:
        overview_revision_repr = OverviewRevisionRepr(
            id=1,
            effective_date_from="2020-01-01T12:00:00",
            effective_date_to=None,
            authority_id=2,
        )

        overview_revision = overview_revision_repr.to_domain()

        assert overview_revision.effective.date_to is None
