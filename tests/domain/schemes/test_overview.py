from datetime import datetime

from schemes.domain.dates import DateRange
from schemes.domain.schemes.overview import FundingProgrammes, OverviewRevision, SchemeOverview, SchemeType


class TestSchemeOverview:
    def test_create(self) -> None:
        overview = SchemeOverview()

        assert overview.overview_revisions == []

    def test_get_overview_revisions_is_copy(self) -> None:
        overview = SchemeOverview()
        overview.update_overviews(
            OverviewRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                name="Wirral Package",
                authority_abbreviation="LIV",
                type_=SchemeType.CONSTRUCTION,
                funding_programme=FundingProgrammes.ATF4,
            )
        )

        overview.overview_revisions.clear()

        assert overview.overview_revisions

    def test_update_overview(self) -> None:
        overview = SchemeOverview()
        overview_revision = OverviewRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1), None),
            name="Wirral Package",
            authority_abbreviation="LIV",
            type_=SchemeType.CONSTRUCTION,
            funding_programme=FundingProgrammes.ATF4,
        )

        overview.update_overview(overview_revision)

        assert overview.overview_revisions == [overview_revision]

    def test_update_overviews(self) -> None:
        overview = SchemeOverview()
        overview_revision1 = OverviewRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1), datetime(2020, 2, 1)),
            name="Wirral Package",
            authority_abbreviation="LIV",
            type_=SchemeType.DEVELOPMENT,
            funding_programme=FundingProgrammes.ATF3,
        )
        overview_revision2 = OverviewRevision(
            id_=2,
            effective=DateRange(datetime(2020, 2, 1), None),
            name="School Streets",
            authority_abbreviation="WYO",
            type_=SchemeType.CONSTRUCTION,
            funding_programme=FundingProgrammes.ATF4,
        )

        overview.update_overviews(overview_revision1, overview_revision2)

        assert overview.overview_revisions == [overview_revision1, overview_revision2]

    def test_get_name(self) -> None:
        overview = SchemeOverview()
        overview.update_overviews(
            OverviewRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), datetime(2020, 2, 1)),
                name="Wirral Package",
                authority_abbreviation="LIV",
                type_=SchemeType.DEVELOPMENT,
                funding_programme=FundingProgrammes.ATF3,
            ),
            OverviewRevision(
                id_=2,
                effective=DateRange(datetime(2020, 2, 1), None),
                name="School Streets",
                authority_abbreviation="WYO",
                type_=SchemeType.CONSTRUCTION,
                funding_programme=FundingProgrammes.ATF4,
            ),
        )

        assert overview.name == "School Streets"

    def test_get_name_when_no_revisions(self) -> None:
        overview = SchemeOverview()

        assert overview.name is None

    def test_get_authority_abbreviation(self) -> None:
        overview = SchemeOverview()
        overview.update_overviews(
            OverviewRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), datetime(2020, 2, 1)),
                name="Wirral Package",
                authority_abbreviation="LIV",
                type_=SchemeType.DEVELOPMENT,
                funding_programme=FundingProgrammes.ATF3,
            ),
            OverviewRevision(
                id_=2,
                effective=DateRange(datetime(2020, 2, 1), None),
                name="School Streets",
                authority_abbreviation="WYO",
                type_=SchemeType.CONSTRUCTION,
                funding_programme=FundingProgrammes.ATF4,
            ),
        )

        assert overview.authority_abbreviation == "WYO"

    def test_get_authority_abbreviation_when_no_revisions(self) -> None:
        overview = SchemeOverview()

        assert overview.authority_abbreviation is None

    def test_get_type(self) -> None:
        overview = SchemeOverview()
        overview.update_overviews(
            OverviewRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), datetime(2020, 2, 1)),
                name="Wirral Package",
                authority_abbreviation="LIV",
                type_=SchemeType.DEVELOPMENT,
                funding_programme=FundingProgrammes.ATF3,
            ),
            OverviewRevision(
                id_=2,
                effective=DateRange(datetime(2020, 2, 1), None),
                name="Wirral Package",
                authority_abbreviation="WYO",
                type_=SchemeType.CONSTRUCTION,
                funding_programme=FundingProgrammes.ATF4,
            ),
        )

        assert overview.type == SchemeType.CONSTRUCTION

    def test_get_type_when_no_revisions(self) -> None:
        overview = SchemeOverview()

        assert overview.type is None

    def test_get_funding_programme(self) -> None:
        overview = SchemeOverview()
        overview.update_overviews(
            OverviewRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), datetime(2020, 2, 1)),
                name="Wirral Package",
                authority_abbreviation="LIV",
                type_=SchemeType.DEVELOPMENT,
                funding_programme=FundingProgrammes.ATF3,
            ),
            OverviewRevision(
                id_=2,
                effective=DateRange(datetime(2020, 2, 1), None),
                name="Wirral Package",
                authority_abbreviation="WYO",
                type_=SchemeType.CONSTRUCTION,
                funding_programme=FundingProgrammes.ATF4,
            ),
        )

        assert overview.funding_programme == FundingProgrammes.ATF4

    def test_get_funding_programme_when_no_revisions(self) -> None:
        overview = SchemeOverview()

        assert overview.funding_programme is None


class TestOverviewRevision:
    def test_create(self) -> None:
        overview_revision = OverviewRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1), None),
            name="Wirral Package",
            authority_abbreviation="LIV",
            type_=SchemeType.CONSTRUCTION,
            funding_programme=FundingProgrammes.ATF4,
        )

        assert (
            overview_revision.id == 1
            and overview_revision.effective == DateRange(datetime(2020, 1, 1), None)
            and overview_revision.name == "Wirral Package"
            and overview_revision.authority_abbreviation == "LIV"
            and overview_revision.type == SchemeType.CONSTRUCTION
            and overview_revision.funding_programme == FundingProgrammes.ATF4
        )
