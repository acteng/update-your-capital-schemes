from datetime import date
from decimal import Decimal

import pytest

from schemes.schemes.domain import (
    DataSource,
    FinancialRevision,
    FinancialType,
    Milestone,
    MilestoneRevision,
    ObservationType,
    Scheme,
)


# TODO: break up Scheme and tests into components
class TestScheme:  # pylint: disable=too-many-public-methods
    def test_get_reference(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

        assert scheme.reference == "ATE00001"

    def test_get_milestone_revisions_is_copy(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_milestone(
            MilestoneRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 1),
            )
        )

        scheme.milestone_revisions.clear()

        assert scheme.milestone_revisions

    def test_update_milestone(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

        scheme.update_milestone(
            MilestoneRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 1),
            )
        )

        assert scheme.milestone_revisions == [
            MilestoneRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 1),
            )
        ]

    def test_get_current_milestone_selects_actual_observation_type(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_milestone(
            MilestoneRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.PLANNED,
                status_date=date(2020, 1, 1),
            )
        )
        scheme.update_milestone(
            MilestoneRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 1),
            )
        )

        assert scheme.current_milestone == Milestone.DETAILED_DESIGN_COMPLETED

    def test_get_current_milestone_selects_latest_milestone(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_milestone(
            MilestoneRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 1),
            )
        )
        scheme.update_milestone(
            MilestoneRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 1),
            )
        )

        assert scheme.current_milestone == Milestone.CONSTRUCTION_STARTED

    def test_get_current_milestone_selects_latest_revision(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_milestone(
            MilestoneRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=date(2020, 2, 1),
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
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal("100000"),
                source=DataSource.ATF4_BID,
            )
        )

        scheme.financial_revisions.clear()

        assert scheme.financial_revisions

    def test_update_financial(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

        scheme.update_financial(
            FinancialRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal("100000"),
                source=DataSource.ATF4_BID,
            )
        )

        assert scheme.financial_revisions == [
            FinancialRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal("100000"),
                source=DataSource.ATF4_BID,
            )
        ]

    def test_get_funding_allocation_sums_amounts(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_financial(
            FinancialRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal("100000"),
                source=DataSource.ATF4_BID,
            )
        )
        scheme.update_financial(
            FinancialRevision(
                effective_date_from=date(2020, 2, 1),
                effective_date_to=None,
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal("200000"),
                source=DataSource.ATF4E_BID,
            )
        )

        assert scheme.funding_allocation == Decimal("300000")

    def test_get_funding_allocation_selects_financial_type(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_financial(
            FinancialRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal("100000"),
                source=DataSource.ATF4_BID,
            )
        )
        scheme.update_financial(
            FinancialRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
                type=FinancialType.EXPECTED_COST,
                amount=Decimal("200000"),
                source=DataSource.ATF4_BID,
            )
        )

        assert scheme.funding_allocation == Decimal("100000")

    def test_get_funding_allocation_selects_latest_revision(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_financial(
            FinancialRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=date(2020, 1, 31),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal("100000"),
                source=DataSource.ATF4_BID,
            )
        )
        scheme.update_financial(
            FinancialRevision(
                effective_date_from=date(2020, 2, 1),
                effective_date_to=None,
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal("200000"),
                source=DataSource.ATF4_BID,
            )
        )

        assert scheme.funding_allocation == Decimal("200000")

    def test_get_funding_allocation_when_no_matching_revisions(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_financial(
            FinancialRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
                type=FinancialType.EXPECTED_COST,
                amount=Decimal("100000"),
                source=DataSource.ATF4_BID,
            )
        )

        assert scheme.funding_allocation is None

    def test_get_funding_allocation_when_no_revisions(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

        assert scheme.funding_allocation is None

    def test_get_spend_to_date_sums_amounts(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_financial(
            FinancialRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
                type=FinancialType.SPENT_TO_DATE,
                amount=Decimal("100000"),
                source=DataSource.ATF4_BID,
            )
        )
        scheme.update_financial(
            FinancialRevision(
                effective_date_from=date(2020, 2, 1),
                effective_date_to=None,
                type=FinancialType.SPENT_TO_DATE,
                amount=Decimal("200000"),
                source=DataSource.ATF4E_BID,
            )
        )

        assert scheme.spend_to_date == Decimal("300000")

    def test_get_spend_to_date_selects_financial_type(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_financial(
            FinancialRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
                type=FinancialType.SPENT_TO_DATE,
                amount=Decimal("100000"),
                source=DataSource.ATF4_BID,
            )
        )
        scheme.update_financial(
            FinancialRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
                type=FinancialType.EXPECTED_COST,
                amount=Decimal("200000"),
                source=DataSource.ATF4_BID,
            )
        )

        assert scheme.spend_to_date == Decimal("100000")

    def test_get_spend_to_date_selects_latest_revision(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_financial(
            FinancialRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=date(2020, 1, 31),
                type=FinancialType.SPENT_TO_DATE,
                amount=Decimal("100000"),
                source=DataSource.ATF4_BID,
            )
        )
        scheme.update_financial(
            FinancialRevision(
                effective_date_from=date(2020, 2, 1),
                effective_date_to=None,
                type=FinancialType.SPENT_TO_DATE,
                amount=Decimal("200000"),
                source=DataSource.ATF4_BID,
            )
        )

        assert scheme.spend_to_date == Decimal("200000")

    def test_get_spend_to_date_when_no_matching_revisions(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_financial(
            FinancialRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
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
        scheme.update_financial(
            FinancialRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
                type=FinancialType.CHANGE_CONTROL_FUNDING_REALLOCATION,
                amount=Decimal("10000"),
                source=DataSource.CHANGE_CONTROL,
            )
        )
        scheme.update_financial(
            FinancialRevision(
                effective_date_from=date(2020, 2, 1),
                effective_date_to=None,
                type=FinancialType.CHANGE_CONTROL_FUNDING_REALLOCATION,
                amount=Decimal("20000"),
                source=DataSource.CHANGE_CONTROL,
            )
        )

        assert scheme.change_control_adjustment == Decimal("30000")

    def test_get_change_control_adjustment_selects_source(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_financial(
            FinancialRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
                type=FinancialType.CHANGE_CONTROL_FUNDING_REALLOCATION,
                amount=Decimal("10000"),
                source=DataSource.CHANGE_CONTROL,
            )
        )
        scheme.update_financial(
            FinancialRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal("20000"),
                source=DataSource.ATF4_BID,
            )
        )

        assert scheme.change_control_adjustment == Decimal("10000")

    def test_get_change_control_adjustment_selects_latest_revision(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_financial(
            FinancialRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=date(2020, 1, 31),
                type=FinancialType.CHANGE_CONTROL_FUNDING_REALLOCATION,
                amount=Decimal("10000"),
                source=DataSource.CHANGE_CONTROL,
            )
        )
        scheme.update_financial(
            FinancialRevision(
                effective_date_from=date(2020, 2, 1),
                effective_date_to=None,
                type=FinancialType.CHANGE_CONTROL_FUNDING_REALLOCATION,
                amount=Decimal("20000"),
                source=DataSource.CHANGE_CONTROL,
            )
        )

        assert scheme.change_control_adjustment == Decimal("20000")

    def test_get_change_control_adjustment_when_no_matching_revisions(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_financial(
            FinancialRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
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
        scheme.update_financial(
            FinancialRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal("100000"),
                source=DataSource.ATF4_BID,
            )
        )
        scheme.update_financial(
            FinancialRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
                type=FinancialType.SPENT_TO_DATE,
                amount=Decimal("50000"),
                source=DataSource.ATF4_BID,
            )
        )
        scheme.update_financial(
            FinancialRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
                type=FinancialType.CHANGE_CONTROL_FUNDING_REALLOCATION,
                amount=Decimal("10000"),
                source=DataSource.CHANGE_CONTROL,
            )
        )

        assert scheme.allocation_still_to_spend == Decimal("60000")

    def test_get_allocation_still_to_spend_when_no_funding_allocation(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_financial(
            FinancialRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
                type=FinancialType.SPENT_TO_DATE,
                amount=Decimal("50000"),
                source=DataSource.ATF4_BID,
            )
        )
        scheme.update_financial(
            FinancialRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
                type=FinancialType.CHANGE_CONTROL_FUNDING_REALLOCATION,
                amount=Decimal("10000"),
                source=DataSource.CHANGE_CONTROL,
            )
        )

        assert scheme.allocation_still_to_spend == Decimal("-40000")

    def test_get_allocation_still_to_spend_when_no_spend_to_date(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_financial(
            FinancialRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal("100000"),
                source=DataSource.ATF4_BID,
            )
        )
        scheme.update_financial(
            FinancialRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
                type=FinancialType.CHANGE_CONTROL_FUNDING_REALLOCATION,
                amount=Decimal("10000"),
                source=DataSource.CHANGE_CONTROL,
            )
        )

        assert scheme.allocation_still_to_spend == Decimal("110000")

    def test_get_allocation_still_to_spend_when_no_change_control_adjustment(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_financial(
            FinancialRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal("100000"),
                source=DataSource.ATF4_BID,
            )
        )
        scheme.update_financial(
            FinancialRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
                type=FinancialType.SPENT_TO_DATE,
                amount=Decimal("50000"),
                source=DataSource.ATF4_BID,
            )
        )

        assert scheme.allocation_still_to_spend == Decimal("50000")

    def test_get_allocation_still_to_spend_when_no_revisions(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

        assert scheme.allocation_still_to_spend == Decimal("0")


class TestMilestoneRevision:
    @pytest.mark.parametrize(
        "effective_date_from, effective_date_to",
        [(date(2020, 1, 1), date(2020, 1, 31)), (date(2020, 1, 31), date(2020, 1, 31)), (date(2020, 1, 1), None)],
    )
    def test_effective_date_from_before_or_equal_to_effective_date_to(
        self, effective_date_from: date, effective_date_to: date | None
    ) -> None:
        MilestoneRevision(
            effective_date_from=effective_date_from,
            effective_date_to=effective_date_to,
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 1, 1),
        )

    def test_effective_date_from_after_effective_date_to_errors(self) -> None:
        with pytest.raises(
            ValueError, match="Effective date from '2020-01-01' must not be after effective date to '2019-12-31'"
        ):
            MilestoneRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=date(2019, 12, 31),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 1),
            )


class TestFinancialRevision:
    @pytest.mark.parametrize(
        "effective_date_from, effective_date_to",
        [(date(2020, 1, 1), date(2020, 1, 31)), (date(2020, 1, 31), date(2020, 1, 31)), (date(2020, 1, 1), None)],
    )
    def test_effective_date_from_before_or_equal_to_effective_date_to(
        self, effective_date_from: date, effective_date_to: date | None
    ) -> None:
        FinancialRevision(
            effective_date_from=effective_date_from,
            effective_date_to=effective_date_to,
            type=FinancialType.FUNDING_ALLOCATION,
            amount=Decimal("100000"),
            source=DataSource.ATF4_BID,
        )

    def test_effective_date_from_after_effective_date_to_errors(self) -> None:
        with pytest.raises(
            ValueError, match="Effective date from '2020-01-01' must not be after effective date to '2019-12-31'"
        ):
            FinancialRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=date(2019, 12, 31),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal("100000"),
                source=DataSource.ATF4_BID,
            )
