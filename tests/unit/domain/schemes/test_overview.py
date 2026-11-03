from schemes.domain.schemes.overview import FundingProgrammes, OverviewRevision, SchemeOverview


class TestSchemeOverview:
    def test_create(self) -> None:
        overview_revision = OverviewRevision(
            name="Wirral Package", authority_abbreviation="LIV", funding_programme=FundingProgrammes.ATF4
        )

        overview = SchemeOverview(overview_revision)

        assert overview.overview_revision == overview_revision

    def test_get_name(self) -> None:
        overview = SchemeOverview(
            OverviewRevision(
                name="Wirral Package", authority_abbreviation="LIV", funding_programme=FundingProgrammes.ATF4
            )
        )

        assert overview.name == "Wirral Package"

    def test_get_authority_abbreviation(self) -> None:
        overview = SchemeOverview(
            OverviewRevision(
                name="Wirral Package", authority_abbreviation="LIV", funding_programme=FundingProgrammes.ATF4
            )
        )

        assert overview.authority_abbreviation == "LIV"

    def test_get_funding_programme(self) -> None:
        overview = SchemeOverview(
            OverviewRevision(
                name="Wirral Package", authority_abbreviation="LIV", funding_programme=FundingProgrammes.ATF4
            )
        )

        assert overview.funding_programme == FundingProgrammes.ATF4


class TestOverviewRevision:
    def test_create(self) -> None:
        overview_revision = OverviewRevision(
            name="Wirral Package", authority_abbreviation="LIV", funding_programme=FundingProgrammes.ATF4
        )

        assert (
            overview_revision.name == "Wirral Package"
            and overview_revision.authority_abbreviation == "LIV"
            and overview_revision.funding_programme == FundingProgrammes.ATF4
        )
