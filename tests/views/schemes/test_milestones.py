from datetime import date

import pytest

from schemes.domain.schemes import (
    DateRange,
    Milestone,
    MilestoneRevision,
    ObservationType,
)
from schemes.views.schemes.milestones import (
    MilestoneContext,
    MilestoneRepr,
    MilestoneRevisionRepr,
    SchemeMilestoneRowContext,
    SchemeMilestonesContext,
)
from schemes.views.schemes.observations import ObservationTypeRepr


class TestSchemeMilestonesContext:
    def test_from_domain_sets_milestones(self) -> None:
        context = SchemeMilestonesContext.from_domain([])

        assert [row.milestone for row in context.milestones] == [
            MilestoneContext(name="Feasibility design completed"),
            MilestoneContext(name="Preliminary design completed"),
            MilestoneContext(name="Detailed design completed"),
            MilestoneContext(name="Construction started"),
            MilestoneContext(name="Construction completed"),
        ]

    @pytest.mark.parametrize(
        "milestone, expected_milestone_name",
        [
            (Milestone.FEASIBILITY_DESIGN_COMPLETED, "Feasibility design completed"),
            (Milestone.PRELIMINARY_DESIGN_COMPLETED, "Preliminary design completed"),
            (Milestone.DETAILED_DESIGN_COMPLETED, "Detailed design completed"),
            (Milestone.CONSTRUCTION_STARTED, "Construction started"),
            (Milestone.CONSTRUCTION_COMPLETED, "Construction completed"),
        ],
    )
    def test_from_domain_sets_milestone_dates(self, milestone: Milestone, expected_milestone_name: str) -> None:
        milestone_revisions = [
            MilestoneRevision(
                id_=1,
                effective=DateRange(date(2020, 1, 1), None),
                milestone=milestone,
                observation_type=ObservationType.PLANNED,
                status_date=date(2020, 2, 1),
            ),
            MilestoneRevision(
                id_=2,
                effective=DateRange(date(2020, 1, 1), None),
                milestone=milestone,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 3, 1),
            ),
        ]

        context = SchemeMilestonesContext.from_domain(milestone_revisions)

        assert (
            SchemeMilestoneRowContext(
                milestone=MilestoneContext(name=expected_milestone_name),
                planned=date(2020, 2, 1),
                actual=date(2020, 3, 1),
            )
            in context.milestones
        )

    @pytest.mark.parametrize(
        "expected_milestone_name",
        [
            "Feasibility design completed",
            "Preliminary design completed",
            "Detailed design completed",
            "Construction started",
            "Construction completed",
        ],
    )
    def test_from_domain_sets_milestone_dates_when_no_revisions(self, expected_milestone_name: str) -> None:
        context = SchemeMilestonesContext.from_domain([])

        assert (
            SchemeMilestoneRowContext(
                milestone=MilestoneContext(name=expected_milestone_name), planned=None, actual=None
            )
            in context.milestones
        )


class TestMilestoneContext:
    @pytest.mark.parametrize(
        "milestone, expected_name",
        [
            (Milestone.PUBLIC_CONSULTATION_COMPLETED, "Public consultation completed"),
            (Milestone.FEASIBILITY_DESIGN_COMPLETED, "Feasibility design completed"),
            (Milestone.PRELIMINARY_DESIGN_COMPLETED, "Preliminary design completed"),
            (Milestone.OUTLINE_DESIGN_COMPLETED, "Outline design completed"),
            (Milestone.DETAILED_DESIGN_COMPLETED, "Detailed design completed"),
            (Milestone.CONSTRUCTION_STARTED, "Construction started"),
            (Milestone.CONSTRUCTION_COMPLETED, "Construction completed"),
            (Milestone.INSPECTION, "Inspection"),
            (Milestone.NOT_PROGRESSED, "Not progressed"),
            (Milestone.SUPERSEDED, "Superseded"),
            (Milestone.REMOVED, "Removed"),
            (None, None),
        ],
    )
    def test_from_domain(self, milestone: Milestone | None, expected_name: str | None) -> None:
        context = MilestoneContext.from_domain(milestone)

        assert context == MilestoneContext(name=expected_name)


class TestMilestoneRevisionRepr:
    def test_to_domain(self) -> None:
        milestone_revision_repr = MilestoneRevisionRepr(
            id=1,
            effective_date_from="2020-01-01",
            effective_date_to="2020-01-31",
            milestone=MilestoneRepr.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationTypeRepr.ACTUAL,
            status_date="2020-01-01",
        )

        milestone_revision = milestone_revision_repr.to_domain()

        assert (
            milestone_revision.id == 1
            and milestone_revision.effective == DateRange(date(2020, 1, 1), date(2020, 1, 31))
            and milestone_revision.milestone == Milestone.DETAILED_DESIGN_COMPLETED
            and milestone_revision.observation_type == ObservationType.ACTUAL
            and milestone_revision.status_date == date(2020, 1, 1)
        )

    def test_to_domain_when_no_effective_date_to(self) -> None:
        milestone_revision_repr = MilestoneRevisionRepr(
            id=1,
            effective_date_from="2020-01-01",
            effective_date_to=None,
            milestone=MilestoneRepr.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationTypeRepr.ACTUAL,
            status_date="2020-01-01",
        )

        milestone_revision = milestone_revision_repr.to_domain()

        assert milestone_revision.effective.date_to is None


class TestMilestoneRepr:
    @pytest.mark.parametrize(
        "milestone, expected_milestone",
        [
            ("public consultation completed", Milestone.PUBLIC_CONSULTATION_COMPLETED),
            ("feasibility design started", Milestone.FEASIBILITY_DESIGN_STARTED),
            ("feasibility design completed", Milestone.FEASIBILITY_DESIGN_COMPLETED),
            ("preliminary design completed", Milestone.PRELIMINARY_DESIGN_COMPLETED),
            ("outline design completed", Milestone.OUTLINE_DESIGN_COMPLETED),
            ("detailed design completed", Milestone.DETAILED_DESIGN_COMPLETED),
            ("construction started", Milestone.CONSTRUCTION_STARTED),
            ("construction completed", Milestone.CONSTRUCTION_COMPLETED),
            ("inspection", Milestone.INSPECTION),
            ("not progressed", Milestone.NOT_PROGRESSED),
            ("superseded", Milestone.SUPERSEDED),
            ("removed", Milestone.REMOVED),
        ],
    )
    def test_to_domain(self, milestone: str, expected_milestone: Milestone) -> None:
        assert MilestoneRepr(milestone).to_domain() == expected_milestone
