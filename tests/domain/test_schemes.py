import re
from datetime import date
from decimal import Decimal

import pytest

from schemes.domain.schemes import (
    DataSource,
    DateRange,
    FinancialRevision,
    FinancialType,
    Milestone,
    MilestoneRevision,
    ObservationType,
    Scheme,
)


class TestScheme:
    def test_get_reference(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

        assert scheme.reference == "ATE00001"

    def test_get_milestone_revisions_is_copy(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_milestone(
            MilestoneRevision(
                effective=DateRange(date(2020, 1, 1), None),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 1),
            )
        )

        scheme.milestone_revisions.clear()

        assert scheme.milestone_revisions

    def test_update_milestone(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        milestone_revision = MilestoneRevision(
            effective=DateRange(date(2020, 1, 1), None),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 1, 1),
        )

        scheme.update_milestone(milestone_revision)

        assert scheme.milestone_revisions == [milestone_revision]

    def test_update_milestones(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        milestone_revision1 = MilestoneRevision(
            effective=DateRange(date(2020, 1, 1), None),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 1, 1),
        )
        milestone_revision2 = MilestoneRevision(
            effective=DateRange(date(2020, 1, 1), None),
            milestone=Milestone.CONSTRUCTION_STARTED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 2, 1),
        )

        scheme.update_milestones(milestone_revision1, milestone_revision2)

        assert scheme.milestone_revisions == [milestone_revision1, milestone_revision2]

    def test_get_current_milestone_selects_actual_observation_type(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_milestones(
            MilestoneRevision(
                effective=DateRange(date(2020, 1, 1), None),
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.PLANNED,
                status_date=date(2020, 1, 1),
            ),
            MilestoneRevision(
                effective=DateRange(date(2020, 1, 1), None),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 1),
            ),
        )

        assert scheme.current_milestone == Milestone.DETAILED_DESIGN_COMPLETED

    def test_get_current_milestone_selects_latest_milestone(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_milestones(
            MilestoneRevision(
                effective=DateRange(date(2020, 1, 1), None),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 1),
            ),
            MilestoneRevision(
                effective=DateRange(date(2020, 1, 1), None),
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 1),
            ),
        )

        assert scheme.current_milestone == Milestone.CONSTRUCTION_STARTED

    def test_get_current_milestone_selects_latest_revision(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_milestone(
            MilestoneRevision(
                effective=DateRange(date(2020, 1, 1), date(2020, 2, 1)),
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 1),
            )
        )

        assert scheme.current_milestone is None

    def test_get_current_milestone_when_no_revisions(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

        assert scheme.current_milestone is None

    def test_get_financial_revisions_is_copy(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_financial(
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal("100000"),
                source=DataSource.ATF4_BID,
            )
        )

        scheme.financial_revisions.clear()

        assert scheme.financial_revisions

    def test_update_financial(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        financial_revision = FinancialRevision(
            effective=DateRange(date(2020, 1, 1), None),
            type=FinancialType.FUNDING_ALLOCATION,
            amount=Decimal("100000"),
            source=DataSource.ATF4_BID,
        )

        scheme.update_financial(financial_revision)

        assert scheme.financial_revisions == [financial_revision]

    def test_cannot_update_financial_with_another_current_funding_allocation(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        financial_revision = FinancialRevision(
            effective=DateRange(date(2020, 1, 1), None),
            type=FinancialType.FUNDING_ALLOCATION,
            amount=Decimal("100000"),
            source=DataSource.ATF4_BID,
        )
        scheme.update_financial(financial_revision)

        with pytest.raises(
            ValueError, match=re.escape(f"Current funding allocation already exists: {repr(financial_revision)}")
        ):
            scheme.update_financial(
                FinancialRevision(
                    effective=DateRange(date(2020, 1, 1), None),
                    type=FinancialType.FUNDING_ALLOCATION,
                    amount=Decimal("200000"),
                    source=DataSource.ATF4_BID,
                )
            )

    def test_cannot_update_financial_with_another_current_spent_to_date(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        financial_revision = FinancialRevision(
            effective=DateRange(date(2020, 1, 1), None),
            type=FinancialType.SPENT_TO_DATE,
            amount=Decimal("100000"),
            source=DataSource.ATF4_BID,
        )
        scheme.update_financial(financial_revision)

        with pytest.raises(
            ValueError, match=re.escape(f"Current spent to date already exists: {repr(financial_revision)}")
        ):
            scheme.update_financial(
                FinancialRevision(
                    effective=DateRange(date(2020, 1, 1), None),
                    type=FinancialType.SPENT_TO_DATE,
                    amount=Decimal("200000"),
                    source=DataSource.ATF4_BID,
                )
            )

    def test_update_financials(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        financial_revision1 = FinancialRevision(
            effective=DateRange(date(2020, 1, 1), None),
            type=FinancialType.FUNDING_ALLOCATION,
            amount=Decimal("100000"),
            source=DataSource.ATF4_BID,
        )
        financial_revision2 = FinancialRevision(
            effective=DateRange(date(2020, 1, 1), None),
            type=FinancialType.EXPECTED_COST,
            amount=Decimal("200000"),
            source=DataSource.ATF4_BID,
        )

        scheme.update_financials(financial_revision1, financial_revision2)

        assert scheme.financial_revisions == [financial_revision1, financial_revision2]

    def test_get_funding_allocation(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_financial(
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal("100000"),
                source=DataSource.ATF4_BID,
            )
        )

        assert scheme.funding_allocation == Decimal("100000")

    def test_get_funding_allocation_selects_financial_type(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_financials(
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal("100000"),
                source=DataSource.ATF4_BID,
            ),
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.EXPECTED_COST,
                amount=Decimal("200000"),
                source=DataSource.ATF4_BID,
            ),
        )

        assert scheme.funding_allocation == Decimal("100000")

    def test_get_funding_allocation_selects_source(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_financials(
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal("100000"),
                source=DataSource.ATF4_BID,
            ),
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal("200000"),
                source=DataSource.CHANGE_CONTROL,
            ),
        )

        assert scheme.funding_allocation == Decimal("100000")

    def test_get_funding_allocation_selects_latest_revision(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_financials(
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), date(2020, 1, 31)),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal("100000"),
                source=DataSource.ATF4_BID,
            ),
            FinancialRevision(
                effective=DateRange(date(2020, 2, 1), None),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal("200000"),
                source=DataSource.ATF4_BID,
            ),
        )

        assert scheme.funding_allocation == Decimal("200000")

    def test_get_funding_allocation_when_no_matching_revisions(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_financial(
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.EXPECTED_COST,
                amount=Decimal("100000"),
                source=DataSource.ATF4_BID,
            )
        )

        assert scheme.funding_allocation is None

    def test_get_funding_allocation_when_no_revisions(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

        assert scheme.funding_allocation is None

    def test_get_spend_to_date(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_financial(
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.SPENT_TO_DATE,
                amount=Decimal("100000"),
                source=DataSource.ATF4_BID,
            )
        )

        assert scheme.spend_to_date == Decimal("100000")

    def test_get_spend_to_date_selects_financial_type(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_financials(
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.SPENT_TO_DATE,
                amount=Decimal("100000"),
                source=DataSource.ATF4_BID,
            ),
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.EXPECTED_COST,
                amount=Decimal("200000"),
                source=DataSource.ATF4_BID,
            ),
        )

        assert scheme.spend_to_date == Decimal("100000")

    def test_get_spend_to_date_selects_latest_revision(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_financials(
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), date(2020, 1, 31)),
                type=FinancialType.SPENT_TO_DATE,
                amount=Decimal("100000"),
                source=DataSource.ATF4_BID,
            ),
            FinancialRevision(
                effective=DateRange(date(2020, 2, 1), None),
                type=FinancialType.SPENT_TO_DATE,
                amount=Decimal("200000"),
                source=DataSource.ATF4_BID,
            ),
        )

        assert scheme.spend_to_date == Decimal("200000")

    def test_get_spend_to_date_when_no_matching_revisions(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_financial(
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.EXPECTED_COST,
                amount=Decimal("100000"),
                source=DataSource.ATF4_BID,
            )
        )

        assert scheme.spend_to_date is None

    def test_get_spend_to_date_when_no_revisions(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

        assert scheme.spend_to_date is None

    def test_get_change_control_adjustment_sums_amounts(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_financials(
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal("10000"),
                source=DataSource.CHANGE_CONTROL,
            ),
            FinancialRevision(
                effective=DateRange(date(2020, 2, 1), None),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal("20000"),
                source=DataSource.CHANGE_CONTROL,
            ),
        )

        assert scheme.change_control_adjustment == Decimal("30000")

    def test_get_change_control_adjustment_selects_financial_type(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_financials(
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal("10000"),
                source=DataSource.CHANGE_CONTROL,
            ),
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.EXPECTED_COST,
                amount=Decimal("20000"),
                source=DataSource.CHANGE_CONTROL,
            ),
        )

        assert scheme.change_control_adjustment == Decimal("10000")

    def test_get_change_control_adjustment_selects_source(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_financials(
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal("10000"),
                source=DataSource.CHANGE_CONTROL,
            ),
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal("20000"),
                source=DataSource.ATF4_BID,
            ),
        )

        assert scheme.change_control_adjustment == Decimal("10000")

    def test_get_change_control_adjustment_selects_latest_revision(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_financials(
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), date(2020, 1, 31)),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal("10000"),
                source=DataSource.CHANGE_CONTROL,
            ),
            FinancialRevision(
                effective=DateRange(date(2020, 2, 1), None),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal("20000"),
                source=DataSource.CHANGE_CONTROL,
            ),
        )

        assert scheme.change_control_adjustment == Decimal("20000")

    def test_get_change_control_adjustment_when_no_matching_revisions(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_financial(
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal("10000"),
                source=DataSource.ATF4_BID,
            )
        )

        assert scheme.change_control_adjustment is None

    def test_get_change_control_adjustment_when_no_revisions(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

        assert scheme.change_control_adjustment is None

    def test_get_allocation_still_to_spend(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_financials(
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal("100000"),
                source=DataSource.ATF4_BID,
            ),
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.SPENT_TO_DATE,
                amount=Decimal("50000"),
                source=DataSource.ATF4_BID,
            ),
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal("10000"),
                source=DataSource.CHANGE_CONTROL,
            ),
        )

        assert scheme.allocation_still_to_spend == Decimal("60000")

    def test_get_allocation_still_to_spend_when_no_funding_allocation(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_financials(
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.SPENT_TO_DATE,
                amount=Decimal("50000"),
                source=DataSource.ATF4_BID,
            ),
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal("10000"),
                source=DataSource.CHANGE_CONTROL,
            ),
        )

        assert scheme.allocation_still_to_spend == Decimal("-40000")

    def test_get_allocation_still_to_spend_when_no_spend_to_date(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_financials(
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal("100000"),
                source=DataSource.ATF4_BID,
            ),
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal("10000"),
                source=DataSource.CHANGE_CONTROL,
            ),
        )

        assert scheme.allocation_still_to_spend == Decimal("110000")

    def test_get_allocation_still_to_spend_when_no_change_control_adjustment(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_financials(
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal("100000"),
                source=DataSource.ATF4_BID,
            ),
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.SPENT_TO_DATE,
                amount=Decimal("50000"),
                source=DataSource.ATF4_BID,
            ),
        )

        assert scheme.allocation_still_to_spend == Decimal("50000")

    def test_get_allocation_still_to_spend_when_no_revisions(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

        assert scheme.allocation_still_to_spend == Decimal("0")


class TestDateRange:
    @pytest.mark.parametrize(
        "date_from, date_to",
        [(date(2020, 1, 1), date(2020, 1, 31)), (date(2020, 1, 31), date(2020, 1, 31)), (date(2020, 1, 1), None)],
    )
    def test_date_from_before_or_equal_to_date_to(self, date_from: date, date_to: date | None) -> None:
        DateRange(date_from, date_to)

    def test_date_from_after_date_to_errors(self) -> None:
        with pytest.raises(ValueError, match="From date '2020-01-01' must not be after to date '2019-12-31'"):
            DateRange(date(2020, 1, 1), date(2019, 12, 31))
