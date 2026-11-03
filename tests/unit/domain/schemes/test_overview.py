from schemes.domain.schemes.overview import FundingProgrammes, OverviewRevision


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
