from pydantic import AnyUrl

from schemes.domain.schemes.data_sources import DataSource
from schemes.domain.schemes.financials import SchemeSpend
from schemes.domain.schemes.overview import FundingProgrammes
from schemes.infrastructure.api.collections import CollectionModel
from schemes.infrastructure.api.data_sources import DataSourceModel
from schemes.infrastructure.api.funding_programmes import FundingProgrammeModel
from schemes.infrastructure.api.schemes.financials import (
    CapitalSchemeFinancialsModel,
    CapitalSchemeFundingModel,
    CapitalSchemeSpendModel,
)


class TestCapitalSchemeFundingModel:
    def test_to_domain(self) -> None:
        funding_programme_model = FundingProgrammeModel(
            id=AnyUrl("https://api.example/funding-programmes/ATF4"), code="ATF4", eligible_for_authority_update=True
        )
        funding_model = CapitalSchemeFundingModel(
            funding_programme=AnyUrl("https://api.example/funding-programmes/ATF4"),
            amount=100_000,
            source=DataSourceModel.ATF4_BID,
        )

        funding = funding_model.to_domain([funding_programme_model])

        assert (
            funding.funding_programme == FundingProgrammes.ATF4
            and funding.amount == 100_000
            and funding.source == DataSource.ATF4_BID
        )


class TestCapitalSchemeSpendModel:
    def test_from_domain(self) -> None:
        spend = SchemeSpend(id_=1, amount=50_000, source=DataSource.ATF4_BID)

        spend_model = CapitalSchemeSpendModel.from_domain(spend)

        assert spend_model == CapitalSchemeSpendModel(amount=50_000, source=DataSourceModel.ATF4_BID)

    def test_to_domain(self) -> None:
        spend_model = CapitalSchemeSpendModel(amount=50_000, source=DataSourceModel.ATF4_BID)

        spend = spend_model.to_domain()

        assert spend.id is not None and spend.amount == 50_000 and spend.source == DataSource.ATF4_BID


class TestCapitalSchemeFinancialsModel:
    def test_to_funding_domain(self) -> None:
        funding_programme_models = [
            FundingProgrammeModel(
                id=AnyUrl("https://api.example/funding-programmes/ATF4"),
                code="ATF4",
                eligible_for_authority_update=True,
            ),
            FundingProgrammeModel(
                id=AnyUrl("https://api.example/funding-programmes/CON"), code="CON", eligible_for_authority_update=True
            ),
        ]
        financials_model = CapitalSchemeFinancialsModel(
            funding=CollectionModel[CapitalSchemeFundingModel](
                items=[
                    CapitalSchemeFundingModel(
                        funding_programme=AnyUrl("https://api.example/funding-programmes/ATF4"),
                        amount=100_000,
                        source=DataSourceModel.ATF4_BID,
                    ),
                    CapitalSchemeFundingModel(
                        funding_programme=AnyUrl("https://api.example/funding-programmes/CON"),
                        amount=20_000,
                        source=DataSourceModel.FUNDING_DEVOLUTION,
                    ),
                ]
            ),
            spend=None,
        )

        funding1, funding2 = financials_model.to_funding_domain(funding_programme_models)

        assert (
            funding1.funding_programme == FundingProgrammes.ATF4
            and funding1.amount == 100_000
            and funding1.source == DataSource.ATF4_BID
        )
        assert (
            funding2.funding_programme == FundingProgrammes.CON
            and funding2.amount == 20_000
            and funding2.source == DataSource.FUNDING_DEVOLUTION
        )

    def test_to_spend_domain(self) -> None:
        financials_model = CapitalSchemeFinancialsModel(
            funding=CollectionModel[CapitalSchemeFundingModel](items=[]),
            spend=CapitalSchemeSpendModel(amount=50_000, source=DataSourceModel.ATF4_BID),
        )

        spend = financials_model.to_spend_domain()

        assert spend and spend.id is not None and spend.amount == 50_000 and spend.source == DataSource.ATF4_BID

    def test_to_spend_domain_when_no_spend(self) -> None:
        financials_model = CapitalSchemeFinancialsModel(
            funding=CollectionModel[CapitalSchemeFundingModel](items=[]), spend=None
        )

        spend = financials_model.to_spend_domain()

        assert not spend
