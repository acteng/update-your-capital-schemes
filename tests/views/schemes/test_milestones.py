from datetime import date, datetime

import pytest
from flask import Flask
from flask_wtf.csrf import generate_csrf
from werkzeug.datastructures import MultiDict

from schemes.domain.schemes import (
    DataSource,
    DateRange,
    Milestone,
    MilestoneRevision,
    ObservationType,
    Scheme,
    SchemeMilestones,
)
from schemes.views.schemes.funding import DataSourceRepr
from schemes.views.schemes.milestones import (
    ChangeMilestoneDatesContext,
    ChangeMilestoneDatesForm,
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
                effective=DateRange(datetime(2020, 1, 1), None),
                milestone=milestone,
                observation_type=ObservationType.PLANNED,
                status_date=date(2020, 2, 1),
                source=DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                id_=2,
                effective=DateRange(datetime(2020, 1, 1), None),
                milestone=milestone,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 3, 1),
                source=DataSource.ATF4_BID,
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


class TestChangeMilestoneDatesContext:
    def test_from_domain(self, app: Flask) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.milestones.update_milestone(
            MilestoneRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 2),
                source=DataSource.ATF4_BID,
            )
        )

        context = ChangeMilestoneDatesContext.from_domain(scheme)

        assert context.id == 1 and context.form.date.data == date(2020, 1, 2)


class TestChangeMilestoneDatesForm:
    def test_from_domain(self, app: Flask) -> None:
        milestones = SchemeMilestones()
        milestones.update_milestone(
            MilestoneRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 2),
                source=DataSource.ATF4_BID,
            )
        )

        form = ChangeMilestoneDatesForm.from_domain(milestones)

        assert form.date.data == date(2020, 1, 2)

    def test_from_domain_when_minimal(self, app: Flask) -> None:
        milestones = SchemeMilestones()

        form = ChangeMilestoneDatesForm.from_domain(milestones)

        assert form.date.data is None

    def test_update_domain(self, app: Flask) -> None:
        form = ChangeMilestoneDatesForm(data={"date": date(2020, 1, 3)})
        milestones = SchemeMilestones()
        milestones.update_milestone(
            MilestoneRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1, 12), None),
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 2),
                source=DataSource.ATF4_BID,
            )
        )

        form.update_domain(milestones, now=datetime(2020, 1, 31, 13))

        milestone_revision1: MilestoneRevision
        milestone_revision2: MilestoneRevision
        milestone_revision1, milestone_revision2 = milestones.milestone_revisions
        assert milestone_revision1.id == 1 and milestone_revision1.effective.date_to == datetime(2020, 1, 31, 13)
        assert (
            milestone_revision2.effective == DateRange(datetime(2020, 1, 31, 13), None)
            and milestone_revision2.milestone == Milestone.CONSTRUCTION_STARTED
            and milestone_revision2.observation_type == ObservationType.ACTUAL
            and milestone_revision2.status_date == date(2020, 1, 3)
            and milestone_revision2.source == DataSource.AUTHORITY_UPDATE
        )

    def test_update_domain_preserves_dates_with_empty_date(self, app: Flask) -> None:
        form = ChangeMilestoneDatesForm(data={"date": None})
        milestones = SchemeMilestones()
        milestones.update_milestones(
            MilestoneRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1, 12), None),
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 2),
                source=DataSource.ATF4_BID,
            )
        )

        form.update_domain(milestones, now=datetime(2020, 1, 31, 13))

        milestone_revision1: MilestoneRevision
        (milestone_revision1,) = milestones.milestone_revisions
        assert (
            milestone_revision1.id == 1
            and milestone_revision1.effective == DateRange(datetime(2020, 1, 1, 12), None)
            and milestone_revision1.milestone == Milestone.CONSTRUCTION_STARTED
            and milestone_revision1.observation_type == ObservationType.ACTUAL
            and milestone_revision1.status_date == date(2020, 1, 2)
            and milestone_revision1.source == DataSource.ATF4_BID
        )

    def test_no_errors_when_valid(self, app: Flask) -> None:
        form = ChangeMilestoneDatesForm(
            formdata=MultiDict([("csrf_token", generate_csrf()), ("date", "2"), ("date", "1"), ("date", "2020")])
        )

        form.validate()

        assert not form.errors

    def test_date_is_optional(self, app: Flask) -> None:
        form = ChangeMilestoneDatesForm(formdata=MultiDict([("date", ""), ("date", ""), ("date", "")]))

        form.validate()

        assert "date" not in form.errors

    @pytest.mark.parametrize(
        "date_",
        [
            ("x", "x", "x"),
            ("99", "1", "2020"),
            ("", "1", "2020"),
            ("2", "", "2020"),
            ("2", "1", ""),
            ("", "", "2020"),
            ("", "1", ""),
            ("2", "", ""),
        ],
    )
    def test_date_is_a_date(self, app: Flask, date_: tuple[str, str, str]) -> None:
        form = ChangeMilestoneDatesForm(
            formdata=MultiDict([("date", date_[0]), ("date", date_[1]), ("date", date_[2])])
        )

        form.validate()

        assert "Construction started actual date must be a real date" in form.errors["date"]


class TestMilestoneRevisionRepr:
    def test_from_domain(self) -> None:
        milestone_revision = MilestoneRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1, 12), datetime(2020, 1, 31, 13)),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 1, 1),
            source=DataSource.ATF4_BID,
        )

        milestone_revision_repr = MilestoneRevisionRepr.from_domain(milestone_revision)

        assert milestone_revision_repr == MilestoneRevisionRepr(
            id=1,
            effective_date_from="2020-01-01T12:00:00",
            effective_date_to="2020-01-31T13:00:00",
            milestone=MilestoneRepr.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationTypeRepr.ACTUAL,
            status_date="2020-01-01",
            source=DataSourceRepr.ATF4_BID,
        )

    def test_cannot_from_domain_when_transient(self) -> None:
        milestone_revision = MilestoneRevision(
            id_=None,
            effective=DateRange(datetime(2020, 1, 1, 12), datetime(2020, 1, 31, 13)),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 1, 1),
            source=DataSource.ATF4_BID,
        )

        with pytest.raises(ValueError, match="Milestone revision must be persistent"):
            MilestoneRevisionRepr.from_domain(milestone_revision)

    def test_from_domain_when_no_effective_date_to(self) -> None:
        milestone_revision = MilestoneRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1), None),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 1, 1),
            source=DataSource.ATF4_BID,
        )

        milestone_revision_repr = MilestoneRevisionRepr.from_domain(milestone_revision)

        assert milestone_revision_repr.effective_date_to is None

    def test_to_domain(self) -> None:
        milestone_revision_repr = MilestoneRevisionRepr(
            id=1,
            effective_date_from="2020-01-01T12:00:00",
            effective_date_to="2020-01-31T13:00:00",
            milestone=MilestoneRepr.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationTypeRepr.ACTUAL,
            status_date="2020-01-01",
            source=DataSourceRepr.ATF4_BID,
        )

        milestone_revision = milestone_revision_repr.to_domain()

        assert (
            milestone_revision.id == 1
            and milestone_revision.effective == DateRange(datetime(2020, 1, 1, 12), datetime(2020, 1, 31, 13))
            and milestone_revision.milestone == Milestone.DETAILED_DESIGN_COMPLETED
            and milestone_revision.observation_type == ObservationType.ACTUAL
            and milestone_revision.status_date == date(2020, 1, 1)
            and milestone_revision.source == DataSource.ATF4_BID
        )

    def test_to_domain_when_no_effective_date_to(self) -> None:
        milestone_revision_repr = MilestoneRevisionRepr(
            id=1,
            effective_date_from="2020-01-01",
            effective_date_to=None,
            milestone=MilestoneRepr.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationTypeRepr.ACTUAL,
            status_date="2020-01-01",
            source=DataSourceRepr.ATF4_BID,
        )

        milestone_revision = milestone_revision_repr.to_domain()

        assert milestone_revision.effective.date_to is None


@pytest.mark.parametrize(
    "milestone, milestone_repr",
    [
        (Milestone.PUBLIC_CONSULTATION_COMPLETED, "public consultation completed"),
        (Milestone.FEASIBILITY_DESIGN_STARTED, "feasibility design started"),
        (Milestone.FEASIBILITY_DESIGN_COMPLETED, "feasibility design completed"),
        (Milestone.PRELIMINARY_DESIGN_COMPLETED, "preliminary design completed"),
        (Milestone.OUTLINE_DESIGN_COMPLETED, "outline design completed"),
        (Milestone.DETAILED_DESIGN_COMPLETED, "detailed design completed"),
        (Milestone.CONSTRUCTION_STARTED, "construction started"),
        (Milestone.CONSTRUCTION_COMPLETED, "construction completed"),
        (Milestone.INSPECTION, "inspection"),
        (Milestone.NOT_PROGRESSED, "not progressed"),
        (Milestone.SUPERSEDED, "superseded"),
        (Milestone.REMOVED, "removed"),
    ],
)
class TestMilestoneRepr:
    def test_from_domain(self, milestone: Milestone, milestone_repr: str) -> None:
        assert MilestoneRepr.from_domain(milestone).value == milestone_repr

    def test_to_domain(self, milestone: Milestone, milestone_repr: str) -> None:
        assert MilestoneRepr(milestone_repr).to_domain() == milestone
