from datetime import date
from decimal import Decimal

import pytest

from schemes.domain.schemes import (
    DataSource,
    DateRange,
    FinancialRevision,
    FinancialType,
    SchemeFunding,
)
from schemes.views.schemes.funding import (
    DataSourceRepr,
    FinancialRevisionRepr,
    FinancialTypeRepr,
    SchemeFundingContext,
)


class TestSchemeFundingContext:
    def test_from_domain_sets_funding_allocation(self) -> None:
        funding = SchemeFunding()
        funding.update_financial(
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal(100000),
                source=DataSource.ATF4_BID,
            )
        )

        context = SchemeFundingContext.from_domain(funding)

        assert context.funding_allocation == Decimal(100000)

    def test_from_domain_sets_spend_to_date(self) -> None:
        funding = SchemeFunding()
        funding.update_financial(
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.SPENT_TO_DATE,
                amount=Decimal(50000),
                source=DataSource.ATF4_BID,
            )
        )

        context = SchemeFundingContext.from_domain(funding)

        assert context.spend_to_date == Decimal(50000)

    def test_from_domain_sets_change_control_adjustment(self) -> None:
        funding = SchemeFunding()
        funding.update_financial(
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal(10000),
                source=DataSource.CHANGE_CONTROL,
            )
        )

        context = SchemeFundingContext.from_domain(funding)

        assert context.change_control_adjustment == Decimal(10000)

    def test_from_domain_sets_allocation_still_to_spend(self) -> None:
        funding = SchemeFunding()
        funding.update_financials(
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal(110000),
                source=DataSource.ATF4_BID,
            ),
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.SPENT_TO_DATE,
                amount=Decimal(50000),
                source=DataSource.ATF4_BID,
            ),
        )

        context = SchemeFundingContext.from_domain(funding)

        assert context.allocation_still_to_spend == Decimal(60000)


class TestFinancialRevisionRepr:
    def test_to_domain(self) -> None:
        financial_revision_repr = FinancialRevisionRepr(
            effective_date_from="2020-01-01",
            effective_date_to="2020-01-31",
            type=FinancialTypeRepr.FUNDING_ALLOCATION,
            amount="100000",
            source=DataSourceRepr.ATF4_BID,
        )

        financial_revision = financial_revision_repr.to_domain()

        assert financial_revision == FinancialRevision(
            effective=DateRange(date(2020, 1, 1), date(2020, 1, 31)),
            type=FinancialType.FUNDING_ALLOCATION,
            amount=Decimal(100000),
            source=DataSource.ATF4_BID,
        )

    def test_to_domain_when_no_effective_date_to(self) -> None:
        financial_revision_repr = FinancialRevisionRepr(
            effective_date_from="2020-01-01",
            effective_date_to=None,
            type=FinancialTypeRepr.FUNDING_ALLOCATION,
            amount="100000",
            source=DataSourceRepr.ATF4_BID,
        )

        financial_revision = financial_revision_repr.to_domain()

        assert financial_revision.effective.date_to is None


class TestFinancialTypeRepr:
    @pytest.mark.parametrize(
        "financial_type, expected_financial_type",
        [
            ("expected cost", FinancialType.EXPECTED_COST),
            ("actual cost", FinancialType.ACTUAL_COST),
            ("funding allocation", FinancialType.FUNDING_ALLOCATION),
            ("spent to date", FinancialType.SPENT_TO_DATE),
            ("funding request", FinancialType.FUNDING_REQUEST),
        ],
    )
    def test_to_domain(self, financial_type: str, expected_financial_type: FinancialType) -> None:
        assert FinancialTypeRepr(financial_type).to_domain() == expected_financial_type


class TestDataSourceRepr:
    @pytest.mark.parametrize(
        "data_source, expected_data_source",
        [
            ("Pulse 5", DataSource.PULSE_5),
            ("Pulse 6", DataSource.PULSE_6),
            ("ATF4 Bid", DataSource.ATF4_BID),
            ("ATF3 Bid", DataSource.ATF3_BID),
            ("Inspectorate review", DataSource.INSPECTORATE_REVIEW),
            ("Regional Engagement Manager review", DataSource.REGIONAL_ENGAGEMENT_MANAGER_REVIEW),
            ("ATE published data", DataSource.ATE_PUBLISHED_DATA),
            ("change control", DataSource.CHANGE_CONTROL),
            ("ATF4e Bid", DataSource.ATF4E_BID),
            ("ATF4e Moderation", DataSource.ATF4E_MODERATION),
            ("Pulse 2023/24 Q2", DataSource.PULSE_2023_24_Q2),
            ("Initial Scheme List", DataSource.INITIAL_SCHEME_LIST),
        ],
    )
    def test_to_domain(self, data_source: str, expected_data_source: DataSource) -> None:
        assert DataSourceRepr(data_source).to_domain() == expected_data_source
