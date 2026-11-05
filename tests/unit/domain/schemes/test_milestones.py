import re
from datetime import date

import pytest

from schemes.domain.schemes.data_sources import DataSource
from schemes.domain.schemes.milestones import Milestone, MilestoneRevision, SchemeMilestones
from schemes.domain.schemes.observations import ObservationType


class TestSchemeMilestones:
    def test_create(self) -> None:
        milestones = SchemeMilestones()

        assert milestones.milestone_revisions == []

    def test_milestones_eligible_for_authority_update(self) -> None:
        milestones = SchemeMilestones()

        assert milestones.milestones_eligible_for_authority_update == {
            Milestone.FEASIBILITY_DESIGN_COMPLETED,
            Milestone.PRELIMINARY_DESIGN_COMPLETED,
            Milestone.DETAILED_DESIGN_COMPLETED,
            Milestone.CONSTRUCTION_STARTED,
            Milestone.CONSTRUCTION_COMPLETED,
        }

    def test_get_milestone_revisions_is_copy(self) -> None:
        milestones = SchemeMilestones()
        milestones.update_milestone(
            MilestoneRevision(
                id_=1,
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 1),
                source=DataSource.ATF4_BID,
            )
        )

        milestones.milestone_revisions.clear()

        assert milestones.milestone_revisions

    def test_update_milestone(self) -> None:
        milestones = SchemeMilestones()
        milestone_revision = MilestoneRevision(
            id_=1,
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 1, 1),
            source=DataSource.ATF4_BID,
        )

        milestones.update_milestone(milestone_revision)

        assert milestones.milestone_revisions == [milestone_revision]

    def test_cannot_update_milestone_with_existing_revision(self) -> None:
        milestones = SchemeMilestones()
        milestone_revision = MilestoneRevision(
            id_=1,
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2000, 1, 1),
            source=DataSource.ATF4_BID,
        )
        milestones.update_milestone(milestone_revision)

        with pytest.raises(ValueError, match=re.escape(f"Milestone already exists: {milestone_revision!r}")):
            milestones.update_milestone(
                MilestoneRevision(
                    id_=2,
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
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 1, 1),
            source=DataSource.ATF4_BID,
        )
        milestone_revision2 = MilestoneRevision(
            id_=2,
            milestone=Milestone.CONSTRUCTION_STARTED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 2, 1),
            source=DataSource.ATF4_BID,
        )

        milestones.update_milestones(milestone_revision1, milestone_revision2)

        assert milestones.milestone_revisions == [milestone_revision1, milestone_revision2]

    def test_update_milestone_date_removes_existing_revision(self) -> None:
        milestones = SchemeMilestones()
        milestones.update_milestone(
            MilestoneRevision(
                id_=1,
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 1),
                source=DataSource.ATF4_BID,
            )
        )

        milestones.update_milestone_date(
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 1, 3),
        )

        assert 1 not in (milestone_revision.id for milestone_revision in milestones.milestone_revisions)

    def test_update_milestone_date_adds_new_revision(self) -> None:
        milestones = SchemeMilestones()

        milestones.update_milestone_date(
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 1, 3),
        )

        (milestone_revision,) = milestones.milestone_revisions
        assert (
            milestone_revision.id is None
            and milestone_revision.milestone == Milestone.DETAILED_DESIGN_COMPLETED
            and milestone_revision.observation_type == ObservationType.ACTUAL
            and milestone_revision.status_date == date(2020, 1, 3)
        )

    def test_get_current_milestone_selects_actual_observation_type(self) -> None:
        milestones = SchemeMilestones()
        milestones.update_milestones(
            MilestoneRevision(
                id_=1,
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.PLANNED,
                status_date=date(2020, 1, 1),
                source=DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                id_=2,
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
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 1),
                source=DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                id_=2,
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 1),
                source=DataSource.ATF4_BID,
            ),
        )

        assert milestones.current_milestone == Milestone.CONSTRUCTION_STARTED

    def test_get_current_milestone_when_no_revisions(self) -> None:
        milestones = SchemeMilestones()

        assert milestones.current_milestone is None

    def test_get_status_date_selects_milestone(self) -> None:
        milestones = SchemeMilestones()
        milestones.update_milestones(
            MilestoneRevision(
                id_=1,
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 1),
                source=DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                id_=2,
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 2, 1),
                source=DataSource.ATF4_BID,
            ),
        )

        status_date = milestones.get_status_date(Milestone.CONSTRUCTION_STARTED, ObservationType.ACTUAL)

        assert status_date == date(2020, 2, 1)

    def test_get_status_date_selects_observation_type(self) -> None:
        milestones = SchemeMilestones()
        milestones.update_milestones(
            MilestoneRevision(
                id_=1,
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.PLANNED,
                status_date=date(2020, 1, 1),
                source=DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                id_=2,
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 2, 1),
                source=DataSource.ATF4_BID,
            ),
        )

        status_date = milestones.get_status_date(Milestone.DETAILED_DESIGN_COMPLETED, ObservationType.ACTUAL)

        assert status_date == date(2020, 2, 1)

    def test_get_status_date_when_no_revisions(self) -> None:
        milestones = SchemeMilestones()

        status_date = milestones.get_status_date(Milestone.CONSTRUCTION_STARTED, ObservationType.ACTUAL)

        assert status_date is None


class TestMilestoneRevision:
    def test_create(self) -> None:
        milestone_revision = MilestoneRevision(
            id_=1,
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 1, 1),
            source=DataSource.ATF4_BID,
        )

        assert (
            milestone_revision.id == 1
            and milestone_revision.milestone == Milestone.DETAILED_DESIGN_COMPLETED
            and milestone_revision.observation_type == ObservationType.ACTUAL
            and milestone_revision.status_date == date(2020, 1, 1)
            and milestone_revision.source == DataSource.ATF4_BID
        )


class TestMilestone:
    @pytest.mark.parametrize(
        "milestone, expected_milestone_order",
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
    def test_milestone_order(self, milestone: Milestone, expected_milestone_order: int) -> None:
        assert milestone.milestone_order == expected_milestone_order
