from schemes.domain.schemes.overview import FundingProgrammes, OverviewRevision, SchemeOverview


class TestSchemeOverview:
    def test_create(self) -> None:
        overview = SchemeOverview()

        assert not overview.overview_revision

    def test_update_overview(self) -> None:
        overview = SchemeOverview()
        overview_revision = OverviewRevision(
            name="Wirral Package", authority_abbreviation="LIV", funding_programme=FundingProgrammes.ATF4
        )

        overview.update_overview(overview_revision)

        assert overview.overview_revision == overview_revision

    def test_get_name(self) -> None:
        overview = SchemeOverview()
        overview.update_overview(
            OverviewRevision(
                name="Wirral Package", authority_abbreviation="LIV", funding_programme=FundingProgrammes.ATF4
            )
        )

        assert overview.name == "Wirral Package"

    def test_get_name_when_no_revision(self) -> None:
        overview = SchemeOverview()

        assert overview.name is None

    def test_get_authority_abbreviation(self) -> None:
        overview = SchemeOverview()
        overview.update_overview(
            OverviewRevision(
                name="Wirral Package", authority_abbreviation="LIV", funding_programme=FundingProgrammes.ATF4
            )
        )

        assert overview.authority_abbreviation == "LIV"

    def test_get_authority_abbreviation_when_no_revision(self) -> None:
        overview = SchemeOverview()

        assert overview.authority_abbreviation is None

    def test_get_funding_programme(self) -> None:
        overview = SchemeOverview()
        overview.update_overview(
            OverviewRevision(
                name="Wirral Package", authority_abbreviation="LIV", funding_programme=FundingProgrammes.ATF4
            )
        )

        assert overview.funding_programme == FundingProgrammes.ATF4

    def test_get_funding_programme_when_no_revision(self) -> None:
        overview = SchemeOverview()

        assert overview.funding_programme is None


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
