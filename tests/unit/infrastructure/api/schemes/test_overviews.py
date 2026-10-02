from pydantic import AnyUrl

from schemes.domain.schemes.overview import FundingProgrammes
from schemes.infrastructure.api.authorities import AuthorityModel
from schemes.infrastructure.api.funding_programmes import FundingProgrammeItemModel
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
        funding_programme_item_model = FundingProgrammeItemModel(
            id=AnyUrl("https://api.example/funding-programmes/ATF4"), code="ATF4"
        )
        overview_model = CapitalSchemeOverviewModel(
            name="Wirral Package",
            funding_programme=AnyUrl("https://api.example/funding-programmes/ATF4"),
            improvement=AnyUrl("https://api.example/improvements/IMP00001"),
        )

        overview_revision = overview_model.to_domain(authority_model, [funding_programme_item_model])

        assert (
            overview_revision.name == "Wirral Package"
            and overview_revision.authority_abbreviation == "LIV"
            and overview_revision.funding_programme == FundingProgrammes.ATF4
        )
