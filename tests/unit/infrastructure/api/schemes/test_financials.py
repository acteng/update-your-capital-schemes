from datetime import datetime

import pytest

from schemes.domain.dates import DateRange
from schemes.domain.schemes.data_sources import DataSource
from schemes.domain.schemes.funding import FinancialRevision, FinancialType
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

        financial_revision = funding_model.to_domain()

        assert (
            financial_revision.id is not None
            and financial_revision.type == FinancialType.FUNDING_ALLOCATION
            and financial_revision.amount == 100_000
            and financial_revision.source == DataSource.ATF4_BID
        )


class TestCapitalSchemeSpendModel:
    def test_from_domain(self) -> None:
        financial_revision = FinancialRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1), datetime(2020, 2, 1)),
            type_=FinancialType.SPEND_TO_DATE,
            amount=50_000,
            source=DataSource.ATF4_BID,
        )

        spend_model = CapitalSchemeSpendModel.from_domain(financial_revision)

        assert spend_model == CapitalSchemeSpendModel(amount=50_000, source=DataSourceModel.ATF4_BID)

    def test_from_domain_when_invalid_financial_type(self) -> None:
        financial_revision = FinancialRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1), datetime(2020, 2, 1)),
            type_=FinancialType.EXPECTED_COST,
            amount=100_000,
            source=DataSource.ATF4_BID,
        )

        with pytest.raises(ValueError, match="Invalid financial type: FinancialType.EXPECTED_COST"):
            CapitalSchemeSpendModel.from_domain(financial_revision)

    def test_to_domain(self) -> None:
        spend_model = CapitalSchemeSpendModel(amount=50_000, source=DataSourceModel.ATF4_BID)

        financial_revision = spend_model.to_domain()

        assert (
            financial_revision.id is not None
            and financial_revision.type == FinancialType.SPEND_TO_DATE
            and financial_revision.amount == 50_000
            and financial_revision.source == DataSource.ATF4_BID
        )


class TestCapitalSchemeFinancialsModel:
    def test_to_domain(self) -> None:
        financials_model = CapitalSchemeFinancialsModel(
            funding=CollectionModel[CapitalSchemeFundingModel](
                items=[CapitalSchemeFundingModel(amount=100_000, source=DataSourceModel.ATF4_BID)]
            ),
            spend=CapitalSchemeSpendModel(amount=50_000, source=DataSourceModel.ATF4_BID),
        )

        financial_revision1, financial_revision2 = financials_model.to_domain()

        assert (
            financial_revision1.id is not None
            and financial_revision1.type == FinancialType.FUNDING_ALLOCATION
            and financial_revision1.amount == 100_000
            and financial_revision1.source == DataSource.ATF4_BID
        )
        assert (
            financial_revision2.id is not None
            and financial_revision2.type == FinancialType.SPEND_TO_DATE
            and financial_revision2.amount == 50_000
            and financial_revision2.source == DataSource.ATF4_BID
        )
