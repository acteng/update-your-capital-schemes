import pytest

from schemes.domain.schemes.data_sources import DataSource
from schemes.domain.schemes.financials import FinancialType, SchemeFinancial
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

        financial = funding_model.to_domain()

        assert (
            financial.id is not None
            and financial.type == FinancialType.FUNDING_ALLOCATION
            and financial.amount == 100_000
            and financial.source == DataSource.ATF4_BID
        )


class TestCapitalSchemeSpendModel:
    def test_from_domain(self) -> None:
        financial = SchemeFinancial(id_=1, type_=FinancialType.SPEND_TO_DATE, amount=50_000, source=DataSource.ATF4_BID)

        spend_model = CapitalSchemeSpendModel.from_domain(financial)

        assert spend_model == CapitalSchemeSpendModel(amount=50_000, source=DataSourceModel.ATF4_BID)

    def test_from_domain_when_invalid_financial_type(self) -> None:
        financial = SchemeFinancial(
            id_=1, type_=FinancialType.EXPECTED_COST, amount=100_000, source=DataSource.ATF4_BID
        )

        with pytest.raises(ValueError, match="Invalid financial type: FinancialType.EXPECTED_COST"):
            CapitalSchemeSpendModel.from_domain(financial)

    def test_to_domain(self) -> None:
        spend_model = CapitalSchemeSpendModel(amount=50_000, source=DataSourceModel.ATF4_BID)

        financial = spend_model.to_domain()

        assert (
            financial.id is not None
            and financial.type == FinancialType.SPEND_TO_DATE
            and financial.amount == 50_000
            and financial.source == DataSource.ATF4_BID
        )


class TestCapitalSchemeFinancialsModel:
    def test_to_domain(self) -> None:
        financials_model = CapitalSchemeFinancialsModel(
            funding=CollectionModel[CapitalSchemeFundingModel](
                items=[CapitalSchemeFundingModel(amount=100_000, source=DataSourceModel.ATF4_BID)]
            ),
            spend=CapitalSchemeSpendModel(amount=50_000, source=DataSourceModel.ATF4_BID),
        )

        financial1, financial2 = financials_model.to_domain()

        assert (
            financial1.id is not None
            and financial1.type == FinancialType.FUNDING_ALLOCATION
            and financial1.amount == 100_000
            and financial1.source == DataSource.ATF4_BID
        )
        assert (
            financial2.id is not None
            and financial2.type == FinancialType.SPEND_TO_DATE
            and financial2.amount == 50_000
            and financial2.source == DataSource.ATF4_BID
        )
