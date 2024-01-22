from datetime import datetime

import pytest

from schemes.domain.schemes import (
    DataSource,
    DateRange,
    FinancialRevision,
    FinancialType,
    Scheme,
    SchemeFunding,
)
from schemes.views.schemes.funding import (
    DataSourceRepr,
    FinancialRevisionRepr,
    FinancialTypeRepr,
    SchemeChangeSpendToDateContext,
    SchemeFundingContext,
)


class TestSchemeFundingContext:
    def test_from_domain_sets_funding_allocation(self) -> None:
        funding = SchemeFunding()
        funding.update_financial(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_=FinancialType.FUNDING_ALLOCATION,
                amount=100_000,
                source=DataSource.ATF4_BID,
            )
        )

        context = SchemeFundingContext.from_domain(funding)

        assert context.funding_allocation == 100_000

    def test_from_domain_sets_change_control_adjustment(self) -> None:
        funding = SchemeFunding()
        funding.update_financial(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_=FinancialType.FUNDING_ALLOCATION,
                amount=10_000,
                source=DataSource.CHANGE_CONTROL,
            )
        )

        context = SchemeFundingContext.from_domain(funding)

        assert context.change_control_adjustment == 10_000

    def test_from_domain_sets_spend_to_date(self) -> None:
        funding = SchemeFunding()
        funding.update_financial(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_=FinancialType.SPENT_TO_DATE,
                amount=50_000,
                source=DataSource.ATF4_BID,
            )
        )

        context = SchemeFundingContext.from_domain(funding)

        assert context.spend_to_date == 50_000

    def test_from_domain_sets_allocation_still_to_spend(self) -> None:
        funding = SchemeFunding()
        funding.update_financials(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_=FinancialType.FUNDING_ALLOCATION,
                amount=110_000,
                source=DataSource.ATF4_BID,
            ),
            FinancialRevision(
                id_=2,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_=FinancialType.SPENT_TO_DATE,
                amount=50_000,
                source=DataSource.ATF4_BID,
            ),
        )

        context = SchemeFundingContext.from_domain(funding)

        assert context.allocation_still_to_spend == 60_000


class TestSchemeChangeSpendToDateContext:
    def test_from_domain(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.funding.update_financial(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1, 12), None),
                type_=FinancialType.SPENT_TO_DATE,
                amount=40_000,
                source=DataSource.ATF4_BID,
            )
        )

        context = SchemeChangeSpendToDateContext.from_domain(scheme)

        assert context == SchemeChangeSpendToDateContext(id=1, amount=40_000)


class TestFinancialRevisionRepr:
    def test_from_domain(self) -> None:
        financial_revision = FinancialRevision(
            id_=2,
            effective=DateRange(datetime(2020, 1, 1, 12), datetime(2020, 1, 31, 13)),
            type_=FinancialType.FUNDING_ALLOCATION,
            amount=100_000,
            source=DataSource.ATF4_BID,
        )

        financial_revision_repr = FinancialRevisionRepr.from_domain(financial_revision)

        assert financial_revision_repr == FinancialRevisionRepr(
            id=2,
            effective_date_from="2020-01-01T12:00:00",
            effective_date_to="2020-01-31T13:00:00",
            type=FinancialTypeRepr.FUNDING_ALLOCATION,
            amount=100_000,
            source=DataSourceRepr.ATF4_BID,
        )

    def test_cannot_from_domain_when_transient(self) -> None:
        financial_revision = FinancialRevision(
            id_=None,
            effective=DateRange(datetime(2020, 1, 1, 12), datetime(2020, 1, 31, 13)),
            type_=FinancialType.FUNDING_ALLOCATION,
            amount=100_000,
            source=DataSource.ATF4_BID,
        )

        with pytest.raises(ValueError, match="Financial revision must be persistent"):
            FinancialRevisionRepr.from_domain(financial_revision)

    def test_from_domain_when_no_effective_date_to(self) -> None:
        financial_revision = FinancialRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1), None),
            type_=FinancialType.FUNDING_ALLOCATION,
            amount=100_000,
            source=DataSource.ATF4_BID,
        )

        financial_revision_repr = FinancialRevisionRepr.from_domain(financial_revision)

        assert financial_revision_repr.effective_date_to is None

    def test_to_domain(self) -> None:
        financial_revision_repr = FinancialRevisionRepr(
            id=1,
            effective_date_from="2020-01-01T12:00:00",
            effective_date_to="2020-01-31T13:00:00",
            type=FinancialTypeRepr.FUNDING_ALLOCATION,
            amount=100_000,
            source=DataSourceRepr.ATF4_BID,
        )

        financial_revision = financial_revision_repr.to_domain()

        assert (
            financial_revision.id == 1
            and financial_revision.effective == DateRange(datetime(2020, 1, 1, 12), datetime(2020, 1, 31, 13))
            and financial_revision.type == FinancialType.FUNDING_ALLOCATION
            and financial_revision.amount == 100_000
            and financial_revision.source == DataSource.ATF4_BID
        )

    def test_to_domain_when_no_effective_date_to(self) -> None:
        financial_revision_repr = FinancialRevisionRepr(
            id=1,
            effective_date_from="2020-01-01",
            effective_date_to=None,
            type=FinancialTypeRepr.FUNDING_ALLOCATION,
            amount=100_000,
            source=DataSourceRepr.ATF4_BID,
        )

        financial_revision = financial_revision_repr.to_domain()

        assert financial_revision.effective.date_to is None


@pytest.mark.parametrize(
    "financial_type, financial_type_repr",
    [
        (FinancialType.EXPECTED_COST, "expected cost"),
        (FinancialType.ACTUAL_COST, "actual cost"),
        (FinancialType.FUNDING_ALLOCATION, "funding allocation"),
        (FinancialType.SPENT_TO_DATE, "spent to date"),
        (FinancialType.FUNDING_REQUEST, "funding request"),
    ],
)
class TestFinancialTypeRepr:
    def test_from_domain(self, financial_type: FinancialType, financial_type_repr: str) -> None:
        assert FinancialTypeRepr.from_domain(financial_type).value == financial_type_repr

    def test_to_domain(self, financial_type: FinancialType, financial_type_repr: str) -> None:
        assert FinancialTypeRepr(financial_type_repr).to_domain() == financial_type


@pytest.mark.parametrize(
    "data_source, data_source_repr",
    [
        (DataSource.PULSE_5, "Pulse 5"),
        (DataSource.PULSE_6, "Pulse 6"),
        (DataSource.ATF4_BID, "ATF4 Bid"),
        (DataSource.ATF3_BID, "ATF3 Bid"),
        (DataSource.INSPECTORATE_REVIEW, "Inspectorate Review"),
        (DataSource.REGIONAL_ENGAGEMENT_MANAGER_REVIEW, "Regional Engagement Manager Review"),
        (DataSource.ATE_PUBLISHED_DATA, "ATE Published Data"),
        (DataSource.CHANGE_CONTROL, "Change Control"),
        (DataSource.ATF4E_BID, "ATF4e Bid"),
        (DataSource.ATF4E_MODERATION, "ATF4e Moderation"),
        (DataSource.PULSE_2023_24_Q2, "Pulse 2023/24 Q2"),
        (DataSource.INITIAL_SCHEME_LIST, "Initial Scheme List"),
        (DataSource.AUTHORITY_UPDATE, "Authority Update"),
        (DataSource.PULSE_2023_24_Q2_DATA_CLEANSE, "Pulse 2023/24 Q2 Data Cleanse"),
    ],
)
class TestDataSourceRepr:
    def test_from_domain(self, data_source: DataSource, data_source_repr: str) -> None:
        assert DataSourceRepr.from_domain(data_source).value == data_source_repr

    def test_to_domain(self, data_source: DataSource, data_source_repr: str) -> None:
        assert DataSourceRepr(data_source_repr).to_domain() == data_source
