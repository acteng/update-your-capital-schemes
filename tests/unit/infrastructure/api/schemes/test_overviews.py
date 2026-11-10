from pydantic import AnyUrl

from schemes.infrastructure.api.authorities import AuthorityModel
from schemes.infrastructure.api.schemes.overviews import CapitalSchemeOverviewModel


class TestCapitalSchemeOverviewModel:
    def test_to_domain(self) -> None:
        authority_model = AuthorityModel(
            id=AnyUrl("https://api.example/authorities/LIV"),
            abbreviation="LIV",
            full_name="Liverpool City Region Combined Authority",
            funding_managed_by_capital_schemes=AnyUrl(
                "https://api.example/authorities/LIV/capital-schemes/funding-managed-by"
            ),
        )
        overview_model = CapitalSchemeOverviewModel(
            name="Wirral Package", improvement=AnyUrl("https://api.example/improvements/IMP00001")
        )

        overview = overview_model.to_domain(authority_model)

        assert overview.name == "Wirral Package" and overview.authority_abbreviation == "LIV"
