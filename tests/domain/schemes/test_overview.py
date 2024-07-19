from datetime import datetime

from schemes.domain.dates import DateRange
from schemes.domain.schemes import OverviewRevision, SchemeOverview


class TestSchemeOverview:
    def test_create(self) -> None:
        overview = SchemeOverview()

        assert overview.overview_revisions == []

    def test_get_overview_revisions_is_copy(self) -> None:
        overview = SchemeOverview()
        overview.update_overviews(
            OverviewRevision(id_=1, effective=DateRange(datetime(2020, 1, 1), None), authority_id=2)
        )

        overview.overview_revisions.clear()

        assert overview.overview_revisions

    def test_update_overview(self) -> None:
        overview = SchemeOverview()
        overview_revision = OverviewRevision(id_=1, effective=DateRange(datetime(2020, 1, 1), None), authority_id=2)

        overview.update_overview(overview_revision)

        assert overview.overview_revisions == [overview_revision]

    def test_update_overviews(self) -> None:
        overview = SchemeOverview()
        overview_revision1 = OverviewRevision(
            id_=1, effective=DateRange(datetime(2020, 1, 1), datetime(2020, 2, 1)), authority_id=1
        )
        overview_revision2 = OverviewRevision(id_=2, effective=DateRange(datetime(2020, 2, 1), None), authority_id=2)

        overview.update_overviews(overview_revision1, overview_revision2)

        assert overview.overview_revisions == [overview_revision1, overview_revision2]

    def test_get_authority_id(self) -> None:
        overview = SchemeOverview()
        overview.update_overviews(
            OverviewRevision(id_=1, effective=DateRange(datetime(2020, 1, 1), datetime(2020, 2, 1)), authority_id=1),
            OverviewRevision(id_=2, effective=DateRange(datetime(2020, 2, 1), None), authority_id=2),
        )

        assert overview.authority_id == 2

    def test_get_authority_id_when_no_revisions(self) -> None:
        overview = SchemeOverview()

        assert overview.authority_id is None


class TestOverviewRevision:
    def test_create(self) -> None:
        overview_revision = OverviewRevision(id_=1, effective=DateRange(datetime(2020, 1, 1), None), authority_id=2)

        assert (
            overview_revision.id == 1
            and overview_revision.effective == DateRange(datetime(2020, 1, 1), None)
            and overview_revision.authority_id == 2
        )
