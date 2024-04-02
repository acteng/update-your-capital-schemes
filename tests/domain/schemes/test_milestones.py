import re
from datetime import date, datetime

import pytest

from schemes.domain.dates import DateRange
from schemes.domain.schemes import (
    DataSource,
    Milestone,
    MilestoneRevision,
    ObservationType,
    SchemeMilestones,
)


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
