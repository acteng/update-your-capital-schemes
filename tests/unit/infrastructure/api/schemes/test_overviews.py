import pytest
from pydantic import AnyUrl

from schemes.domain.schemes.overview import FundingProgrammes, SchemeType
from schemes.infrastructure.api.authorities import AuthorityModel
from schemes.infrastructure.api.funding_programmes import FundingProgrammeItemModel
from schemes.infrastructure.api.schemes.overviews import CapitalSchemeOverviewModel, CapitalSchemeTypeModel


class TestCapitalSchemeTypeModel:
    @pytest.mark.parametrize(
        "type_model, expected_type",
        [
            (CapitalSchemeTypeModel.DEVELOPMENT, SchemeType.DEVELOPMENT),
            (CapitalSchemeTypeModel.CONSTRUCTION, SchemeType.CONSTRUCTION),
        ],
    )
    def test_to_domain(self, type_model: CapitalSchemeTypeModel, expected_type: SchemeType) -> None:
        assert type_model.to_domain() == expected_type


class TestCapitalSchemeOverviewModel:
    def test_to_domain(self) -> None:
        authority_model = AuthorityModel(
            id=AnyUrl("https://api.example/authorities/LIV"),
            abbreviation="LIV",
            full_name="Liverpool City Region Combined Authority",
            bid_submitting_capital_schemes=AnyUrl("https://api.example/authorities/LIV/capital-schemes/bid-submitting"),
        )
        funding_programme_item_model = FundingProgrammeItemModel(
            id=AnyUrl("https://api.example/funding-programmes/ATF4"), code="ATF4"
        )
        overview_model = CapitalSchemeOverviewModel(
            name="Wirral Package",
            bid_submitting_authority=AnyUrl("https://api.example/authorities/LIV"),
            funding_programme=AnyUrl("https://api.example/funding-programmes/ATF4"),
            type=CapitalSchemeTypeModel.CONSTRUCTION,
        )

        overview_revision = overview_model.to_domain([authority_model], [funding_programme_item_model])

        assert (
            overview_revision.name == "Wirral Package"
            and overview_revision.authority_abbreviation == "LIV"
            and overview_revision.funding_programme == FundingProgrammes.ATF4
            and overview_revision.type == SchemeType.CONSTRUCTION
        )
