from schemes.domain.schemes.overview import SchemeOverview


class TestSchemeOverview:
    def test_create(self) -> None:
        overview = SchemeOverview(name="Wirral Package", authority_abbreviation="LIV")

        assert overview.name == "Wirral Package" and overview.authority_abbreviation == "LIV"
