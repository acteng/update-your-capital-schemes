from datetime import date

from schemes.domain.schemes import (
    DateRange,
    Milestone,
    MilestoneRevision,
    ObservationType,
    Scheme,
    SchemeFunding,
)


class TestScheme:
    def test_get_reference(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

        assert scheme.reference == "ATE00001"

    def test_get_funding(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

        assert isinstance(scheme.funding, SchemeFunding)

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

    def test_get_current_milestone_revisions(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        milestone_revision1 = MilestoneRevision(
            effective=DateRange(date(2020, 1, 1), date(2020, 1, 31)),
            milestone=Milestone.PUBLIC_CONSULTATION_COMPLETED,
            observation_type=ObservationType.PLANNED,
            status_date=date(2020, 1, 1),
        )
        milestone_revision2 = MilestoneRevision(
            effective=DateRange(date(2020, 2, 1), None),
            milestone=Milestone.PUBLIC_CONSULTATION_COMPLETED,
            observation_type=ObservationType.PLANNED,
            status_date=date(2020, 2, 1),
        )
        scheme.update_milestones(milestone_revision1, milestone_revision2)

        assert scheme.current_milestone_revisions == [milestone_revision2]

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
