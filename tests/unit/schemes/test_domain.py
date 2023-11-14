from datetime import date

import pytest

from schemes.schemes.domain import Milestone, MilestoneRevision, ObservationType, Scheme


class TestScheme:
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
