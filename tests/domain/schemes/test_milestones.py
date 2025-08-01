import re
from datetime import date, datetime

import pytest

from schemes.domain.dates import DateRange
from schemes.domain.schemes.data_sources import DataSource
from schemes.domain.schemes.milestones import Milestone, MilestoneRevision, SchemeMilestones
from schemes.domain.schemes.observations import ObservationType


class TestSchemeMilestones:
    def test_create(self) -> None:
        milestones = SchemeMilestones()

        assert milestones.milestone_revisions == []

    def test_get_milestone_revisions_is_copy(self) -> None:
        milestones = SchemeMilestones()
        milestones.update_milestone(
            MilestoneRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 1),
                source=DataSource.ATF4_BID,
            )
        )

        milestones.milestone_revisions.clear()

        assert milestones.milestone_revisions

    def test_get_current_milestone_revisions(self) -> None:
        milestones = SchemeMilestones()
        milestone_revision1 = MilestoneRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1), datetime(2020, 2, 1)),
            milestone=Milestone.PUBLIC_CONSULTATION_COMPLETED,
            observation_type=ObservationType.PLANNED,
            status_date=date(2020, 1, 1),
            source=DataSource.ATF4_BID,
        )
        milestone_revision2 = MilestoneRevision(
            id_=2,
            effective=DateRange(datetime(2020, 2, 1), None),
            milestone=Milestone.PUBLIC_CONSULTATION_COMPLETED,
            observation_type=ObservationType.PLANNED,
            status_date=date(2020, 2, 1),
            source=DataSource.ATF4_BID,
        )
        milestones.update_milestones(milestone_revision1, milestone_revision2)

        assert milestones.current_milestone_revisions == [milestone_revision2]

    def test_update_milestone(self) -> None:
        milestones = SchemeMilestones()
        milestone_revision = MilestoneRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1), None),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 1, 1),
            source=DataSource.ATF4_BID,
        )

        milestones.update_milestone(milestone_revision)

        assert milestones.milestone_revisions == [milestone_revision]

    def test_cannot_update_milestone_with_another_current_milestone(self) -> None:
        milestones = SchemeMilestones()
        milestone_revision = MilestoneRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1), None),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2000, 1, 1),
            source=DataSource.ATF4_BID,
        )
        milestones.update_milestone(milestone_revision)

        with pytest.raises(
            ValueError, match=re.escape(f"Current milestone already exists: {repr(milestone_revision)}")
        ):
            milestones.update_milestone(
                MilestoneRevision(
                    id_=2,
                    effective=DateRange(datetime(2020, 1, 1), None),
                    milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                    observation_type=ObservationType.ACTUAL,
                    status_date=date(2000, 2, 1),
                    source=DataSource.ATF4_BID,
                )
            )

    def test_update_milestones(self) -> None:
        milestones = SchemeMilestones()
        milestone_revision1 = MilestoneRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1), None),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 1, 1),
            source=DataSource.ATF4_BID,
        )
        milestone_revision2 = MilestoneRevision(
            id_=2,
            effective=DateRange(datetime(2020, 1, 1), None),
            milestone=Milestone.CONSTRUCTION_STARTED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 2, 1),
            source=DataSource.ATF4_BID,
        )

        milestones.update_milestones(milestone_revision1, milestone_revision2)

        assert milestones.milestone_revisions == [milestone_revision1, milestone_revision2]

    def test_update_milestone_date_closes_existing_revision(self) -> None:
        milestones = SchemeMilestones()
        milestones.update_milestone(
            MilestoneRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 1),
                source=DataSource.ATF4_BID,
            )
        )

        milestones.update_milestone_date(
            now=datetime(2020, 2, 1, 13),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 1, 3),
        )

        milestone_revision = milestones.milestone_revisions[0]
        assert milestone_revision.id == 1 and milestone_revision.effective.date_to == datetime(2020, 2, 1, 13)

    def test_update_milestone_date_adds_new_revision(self) -> None:
        milestones = SchemeMilestones()

        milestones.update_milestone_date(
            now=datetime(2020, 2, 1, 13),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 1, 3),
        )

        milestone_revision = milestones.milestone_revisions[0]
        assert (
            milestone_revision.id is None
            and milestone_revision.effective == DateRange(datetime(2020, 2, 1, 13), None)
            and milestone_revision.milestone == Milestone.DETAILED_DESIGN_COMPLETED
            and milestone_revision.observation_type == ObservationType.ACTUAL
            and milestone_revision.status_date == date(2020, 1, 3)
        )

    def test_get_current_milestone_selects_actual_observation_type(self) -> None:
        milestones = SchemeMilestones()
        milestones.update_milestones(
            MilestoneRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.PLANNED,
                status_date=date(2020, 1, 1),
                source=DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                id_=2,
                effective=DateRange(datetime(2020, 1, 1), None),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 1),
                source=DataSource.ATF4_BID,
            ),
        )

        assert milestones.current_milestone == Milestone.DETAILED_DESIGN_COMPLETED

    def test_get_current_milestone_selects_latest_milestone(self) -> None:
        milestones = SchemeMilestones()
        milestones.update_milestones(
            MilestoneRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 1),
                source=DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                id_=2,
                effective=DateRange(datetime(2020, 1, 1), None),
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 1),
                source=DataSource.ATF4_BID,
            ),
        )

        assert milestones.current_milestone == Milestone.CONSTRUCTION_STARTED

    def test_get_current_milestone_selects_latest_revision(self) -> None:
        milestones = SchemeMilestones()
        milestones.update_milestone(
            MilestoneRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), datetime(2020, 2, 1)),
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 1),
                source=DataSource.ATF4_BID,
            )
        )

        assert milestones.current_milestone is None

    def test_get_current_milestone_when_no_revisions(self) -> None:
        milestones = SchemeMilestones()

        assert milestones.current_milestone is None

    def test_get_current_status_date_selects_latest_revision(self) -> None:
        milestones = SchemeMilestones()
        milestones.update_milestones(
            MilestoneRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), datetime(2020, 2, 1)),
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 1),
                source=DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                id_=2,
                effective=DateRange(datetime(2020, 2, 1), None),
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 2, 1),
                source=DataSource.ATF4_BID,
            ),
        )

        status_date = milestones.get_current_status_date(Milestone.CONSTRUCTION_STARTED, ObservationType.ACTUAL)

        assert status_date == date(2020, 2, 1)

    def test_get_current_status_date_when_no_revisions(self) -> None:
        milestones = SchemeMilestones()

        status_date = milestones.get_current_status_date(Milestone.CONSTRUCTION_STARTED, ObservationType.ACTUAL)

        assert status_date is None


class TestMilestoneRevision:
    def test_create(self) -> None:
        milestone_revision = MilestoneRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1), None),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 1, 1),
            source=DataSource.ATF4_BID,
        )

        assert (
            milestone_revision.id == 1
            and milestone_revision.effective == DateRange(datetime(2020, 1, 1), None)
            and milestone_revision.milestone == Milestone.DETAILED_DESIGN_COMPLETED
            and milestone_revision.observation_type == ObservationType.ACTUAL
            and milestone_revision.status_date == date(2020, 1, 1)
            and milestone_revision.source == DataSource.ATF4_BID
        )

    def test_close(self) -> None:
        milestone_revision = MilestoneRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1), None),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 1, 1),
            source=DataSource.ATF4_BID,
        )

        milestone_revision.close(datetime(2020, 2, 1))

        assert milestone_revision.effective == DateRange(datetime(2020, 1, 1), datetime(2020, 2, 1))


class TestMilestone:
    @pytest.mark.parametrize(
        "milestone, expected_stage_order",
        [
            (Milestone.PUBLIC_CONSULTATION_COMPLETED, 0),
            (Milestone.FEASIBILITY_DESIGN_STARTED, 1),
            (Milestone.FEASIBILITY_DESIGN_COMPLETED, 2),
            (Milestone.PRELIMINARY_DESIGN_COMPLETED, 3),
            (Milestone.OUTLINE_DESIGN_COMPLETED, 4),
            (Milestone.DETAILED_DESIGN_COMPLETED, 5),
            (Milestone.CONSTRUCTION_STARTED, 6),
            (Milestone.CONSTRUCTION_COMPLETED, 7),
            (Milestone.FUNDING_COMPLETED, 8),
            (Milestone.NOT_PROGRESSED, 9),
            (Milestone.SUPERSEDED, 10),
            (Milestone.REMOVED, 11),
        ],
    )
    def test_stage_order(self, milestone: Milestone, expected_stage_order: int) -> None:
        assert milestone.stage_order == expected_stage_order

    @pytest.mark.parametrize(
        "milestone, expected_is_active",
        [
            (Milestone.PUBLIC_CONSULTATION_COMPLETED, True),
            (Milestone.FEASIBILITY_DESIGN_STARTED, True),
            (Milestone.FEASIBILITY_DESIGN_COMPLETED, True),
            (Milestone.PRELIMINARY_DESIGN_COMPLETED, True),
            (Milestone.OUTLINE_DESIGN_COMPLETED, True),
            (Milestone.DETAILED_DESIGN_COMPLETED, True),
            (Milestone.CONSTRUCTION_STARTED, True),
            (Milestone.CONSTRUCTION_COMPLETED, True),
            (Milestone.FUNDING_COMPLETED, True),
            (Milestone.NOT_PROGRESSED, False),
            (Milestone.SUPERSEDED, False),
            (Milestone.REMOVED, False),
        ],
    )
    def test_is_active(self, milestone: Milestone, expected_is_active: bool) -> None:
        assert milestone.is_active == expected_is_active

    @pytest.mark.parametrize(
        "milestone, expected_is_complete",
        [
            (Milestone.PUBLIC_CONSULTATION_COMPLETED, False),
            (Milestone.FEASIBILITY_DESIGN_STARTED, False),
            (Milestone.FEASIBILITY_DESIGN_COMPLETED, False),
            (Milestone.PRELIMINARY_DESIGN_COMPLETED, False),
            (Milestone.OUTLINE_DESIGN_COMPLETED, False),
            (Milestone.DETAILED_DESIGN_COMPLETED, False),
            (Milestone.CONSTRUCTION_STARTED, False),
            (Milestone.CONSTRUCTION_COMPLETED, False),
            (Milestone.FUNDING_COMPLETED, True),
            (Milestone.NOT_PROGRESSED, False),
            (Milestone.SUPERSEDED, False),
            (Milestone.REMOVED, False),
        ],
    )
    def test_is_complete(self, milestone: Milestone, expected_is_complete: bool) -> None:
        assert milestone.is_complete == expected_is_complete
