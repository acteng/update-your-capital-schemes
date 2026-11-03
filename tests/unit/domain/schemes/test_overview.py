from schemes.domain.schemes.overview import FundingProgrammes, SchemeOverview


class TestSchemeOverview:
    def test_create(self) -> None:
        overview = SchemeOverview(
            name="Wirral Package", authority_abbreviation="LIV", funding_programme=FundingProgrammes.ATF4
        )

        assert (
            overview.name == "Wirral Package"
            and overview.authority_abbreviation == "LIV"
            and overview.funding_programme == FundingProgrammes.ATF4
        )
