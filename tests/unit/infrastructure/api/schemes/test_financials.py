from schemes.domain.schemes.data_sources import DataSource
from schemes.domain.schemes.financials import SchemeSpend
from schemes.infrastructure.api.collections import CollectionModel
from schemes.infrastructure.api.data_sources import DataSourceModel
from schemes.infrastructure.api.schemes.financials import (
    CapitalSchemeFinancialsModel,
    CapitalSchemeFundingModel,
    CapitalSchemeSpendModel,
)


class TestCapitalSchemeFundingModel:
    def test_to_domain(self) -> None:
        funding_model = CapitalSchemeFundingModel(amount=100_000, source=DataSourceModel.ATF4_BID)

        funding = funding_model.to_domain()

        assert funding.amount == 100_000 and funding.source == DataSource.ATF4_BID


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
        financials_model = CapitalSchemeFinancialsModel(
            funding=CollectionModel[CapitalSchemeFundingModel](
                items=[
                    CapitalSchemeFundingModel(amount=100_000, source=DataSourceModel.ATF4_BID),
                    CapitalSchemeFundingModel(amount=20_000, source=DataSourceModel.ATF4_BID),
                ]
            ),
            spend=None,
        )

        funding1, funding2 = financials_model.to_funding_domain()

        assert funding1.amount == 100_000 and funding1.source == DataSource.ATF4_BID
        assert funding2.amount == 20_000 and funding2.source == DataSource.ATF4_BID

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
