from datetime import date, datetime

import pytest
from flask_wtf.csrf import generate_csrf
from werkzeug.datastructures import MultiDict

from schemes.domain.dates import DateRange
from schemes.domain.schemes import (
    DataSource,
    Milestone,
    MilestoneRevision,
    ObservationType,
    SchemeMilestones,
)
from schemes.views.schemes.data_sources import DataSourceRepr
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
from tests.builders import build_scheme


class TestSchemeMilestonesContext:
    def test_from_domain_sets_milestones(self) -> None:
        milestones = SchemeMilestones()

        context = SchemeMilestonesContext.from_domain(milestones)

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
    def test_from_domain_sets_current_milestone_dates(self, milestone: Milestone, expected_milestone_name: str) -> None:
        milestones = SchemeMilestones()
        milestones.update_milestones(
            MilestoneRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), datetime(2020, 2, 1)),
                milestone=milestone,
                observation_type=ObservationType.PLANNED,
                status_date=date(2020, 2, 1),
                source=DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                id_=2,
                effective=DateRange(datetime(2020, 2, 1), None),
                milestone=milestone,
                observation_type=ObservationType.PLANNED,
                status_date=date(2020, 3, 1),
                source=DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                id_=3,
                effective=DateRange(datetime(2020, 1, 1), datetime(2020, 2, 1)),
                milestone=milestone,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 4, 1),
                source=DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                id_=4,
                effective=DateRange(datetime(2020, 2, 1), None),
                milestone=milestone,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 5, 1),
                source=DataSource.ATF4_BID,
            ),
        )

        context = SchemeMilestonesContext.from_domain(milestones)

        assert (
            SchemeMilestoneRowContext(
                milestone=MilestoneContext(name=expected_milestone_name),
                planned=date(2020, 3, 1),
                actual=date(2020, 5, 1),
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
        milestones = SchemeMilestones()

        context = SchemeMilestonesContext.from_domain(milestones)

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
            (Milestone.FEASIBILITY_DESIGN_STARTED, "Feasibility design started"),
            (Milestone.FEASIBILITY_DESIGN_COMPLETED, "Feasibility design completed"),
            (Milestone.PRELIMINARY_DESIGN_COMPLETED, "Preliminary design completed"),
            (Milestone.OUTLINE_DESIGN_COMPLETED, "Outline design completed"),
            (Milestone.DETAILED_DESIGN_COMPLETED, "Detailed design completed"),
            (Milestone.CONSTRUCTION_STARTED, "Construction started"),
            (Milestone.CONSTRUCTION_COMPLETED, "Construction completed"),
            (Milestone.FUNDING_COMPLETED, "Funding completed"),
            (Milestone.NOT_PROGRESSED, "Not progressed"),
            (Milestone.SUPERSEDED, "Superseded"),
            (Milestone.REMOVED, "Removed"),
            (None, None),
        ],
    )
    def test_from_domain(self, milestone: Milestone | None, expected_name: str | None) -> None:
        context = MilestoneContext.from_domain(milestone)

        assert context == MilestoneContext(name=expected_name)


@pytest.mark.usefixtures("app")
class TestChangeMilestoneDatesContext:
    def test_from_domain(self) -> None:
        scheme = build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_id=2)
        scheme.milestones.update_milestone(
            MilestoneRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.PLANNED,
                status_date=date(2020, 1, 2),
                source=DataSource.ATF4_BID,
            )
        )

        context = ChangeMilestoneDatesContext.from_domain(scheme)

        assert (
            context.id == 1
            and context.name == "Wirral Package"
            and context.form.construction_started_planned.data == date(2020, 1, 2)
        )


@pytest.mark.usefixtures("app")
class TestChangeMilestoneDatesForm:
    field_names = [
        "feasibility_design_completed_planned",
        "feasibility_design_completed_actual",
        "preliminary_design_completed_planned",
        "preliminary_design_completed_actual",
        "detailed_design_completed_planned",
        "detailed_design_completed_actual",
        "construction_started_planned",
        "construction_started_actual",
        "construction_completed_planned",
        "construction_completed_actual",
    ]
    field_names_milestones_observation_types = [
        ("feasibility_design_completed_planned", Milestone.FEASIBILITY_DESIGN_COMPLETED, ObservationType.PLANNED),
        ("feasibility_design_completed_actual", Milestone.FEASIBILITY_DESIGN_COMPLETED, ObservationType.ACTUAL),
        ("preliminary_design_completed_planned", Milestone.PRELIMINARY_DESIGN_COMPLETED, ObservationType.PLANNED),
        ("preliminary_design_completed_actual", Milestone.PRELIMINARY_DESIGN_COMPLETED, ObservationType.ACTUAL),
        ("detailed_design_completed_planned", Milestone.DETAILED_DESIGN_COMPLETED, ObservationType.PLANNED),
        ("detailed_design_completed_actual", Milestone.DETAILED_DESIGN_COMPLETED, ObservationType.ACTUAL),
        ("construction_started_planned", Milestone.CONSTRUCTION_STARTED, ObservationType.PLANNED),
        ("construction_started_actual", Milestone.CONSTRUCTION_STARTED, ObservationType.ACTUAL),
        ("construction_completed_planned", Milestone.CONSTRUCTION_COMPLETED, ObservationType.PLANNED),
        ("construction_completed_actual", Milestone.CONSTRUCTION_COMPLETED, ObservationType.ACTUAL),
    ]

    @pytest.mark.parametrize("field_name, milestone, observation_type", field_names_milestones_observation_types)
    def test_from_domain(self, milestone: Milestone, observation_type: ObservationType, field_name: str) -> None:
        milestones = SchemeMilestones()
        milestones.update_milestones(
            MilestoneRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), datetime(2020, 2, 1)),
                milestone=milestone,
                observation_type=observation_type,
                status_date=date(2020, 1, 1),
                source=DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                id_=2,
                effective=DateRange(datetime(2020, 2, 1), None),
                milestone=milestone,
                observation_type=observation_type,
                status_date=date(2020, 2, 1),
                source=DataSource.ATF4_BID,
            ),
        )

        form = ChangeMilestoneDatesForm.from_domain(milestones)

        assert form[field_name].data == date(2020, 2, 1)

    def test_from_domain_when_minimal(self) -> None:
        milestones = SchemeMilestones()

        form = ChangeMilestoneDatesForm.from_domain(milestones)

        assert (
            form.feasibility_design_completed_planned.data is None
            and form.feasibility_design_completed_actual.data is None
            and form.preliminary_design_completed_planned.data is None
            and form.preliminary_design_completed_actual.data is None
            and form.detailed_design_completed_planned.data is None
            and form.detailed_design_completed_actual.data is None
            and form.construction_started_planned.data is None
            and form.construction_started_actual.data is None
            and form.construction_completed_planned.data is None
            and form.construction_completed_actual.data is None
        )

    @pytest.mark.parametrize("field_name, milestone, observation_type", field_names_milestones_observation_types)
    def test_update_domain(self, field_name: str, milestone: Milestone, observation_type: ObservationType) -> None:
        form = ChangeMilestoneDatesForm(
            formdata=MultiDict([(field_name, "3"), (field_name, "1"), (field_name, "2020")])
        )
        milestones = SchemeMilestones()
        milestones.update_milestone(
            MilestoneRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                milestone=milestone,
                observation_type=observation_type,
                status_date=date(2020, 1, 2),
                source=DataSource.ATF4_BID,
            )
        )

        form.update_domain(milestones, now=datetime(2020, 2, 1, 13))

        milestone_revision1: MilestoneRevision
        milestone_revision2: MilestoneRevision
        milestone_revision1, milestone_revision2 = milestones.milestone_revisions
        assert milestone_revision1.id == 1 and milestone_revision1.effective.date_to == datetime(2020, 2, 1, 13)
        assert (
            milestone_revision2.effective == DateRange(datetime(2020, 2, 1, 13), None)
            and milestone_revision2.milestone == milestone
            and milestone_revision2.observation_type == observation_type
            and milestone_revision2.status_date == date(2020, 1, 3)
            and milestone_revision2.source == DataSource.AUTHORITY_UPDATE
        )

    @pytest.mark.parametrize("field_name, milestone, observation_type", field_names_milestones_observation_types)
    def test_update_domain_preserves_dates_with_empty_date(
        self, field_name: str, milestone: Milestone, observation_type: ObservationType
    ) -> None:
        form = ChangeMilestoneDatesForm(formdata=MultiDict([(field_name, ""), (field_name, ""), (field_name, "")]))
        milestones = SchemeMilestones()
        milestones.update_milestones(
            MilestoneRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1, 12), None),
                milestone=milestone,
                observation_type=observation_type,
                status_date=date(2020, 1, 2),
                source=DataSource.ATF4_BID,
            )
        )

        form.update_domain(milestones, now=datetime(2020, 2, 1, 13))

        milestone_revision1: MilestoneRevision
        (milestone_revision1,) = milestones.milestone_revisions
        assert (
            milestone_revision1.id == 1
            and milestone_revision1.effective == DateRange(datetime(2020, 1, 1, 12), None)
            and milestone_revision1.milestone == milestone
            and milestone_revision1.observation_type == observation_type
            and milestone_revision1.status_date == date(2020, 1, 2)
            and milestone_revision1.source == DataSource.ATF4_BID
        )

    @pytest.mark.parametrize("field_name, milestone, observation_type", field_names_milestones_observation_types)
    def test_update_domain_ignores_unchanged_dates(
        self, field_name: str, milestone: Milestone, observation_type: ObservationType
    ) -> None:
        form = ChangeMilestoneDatesForm(
            formdata=MultiDict([(field_name, "2"), (field_name, "1"), (field_name, "2020")])
        )
        milestones = SchemeMilestones()
        milestones.update_milestones(
            MilestoneRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1, 12), None),
                milestone=milestone,
                observation_type=observation_type,
                status_date=date(2020, 1, 2),
                source=DataSource.ATF4_BID,
            )
        )

        form.update_domain(milestones, now=datetime(2020, 2, 1, 13))

        milestone_revision1: MilestoneRevision
        (milestone_revision1,) = milestones.milestone_revisions
        assert (
            milestone_revision1.id == 1
            and milestone_revision1.effective == DateRange(datetime(2020, 1, 1, 12), None)
            and milestone_revision1.milestone == milestone
            and milestone_revision1.observation_type == observation_type
            and milestone_revision1.status_date == date(2020, 1, 2)
            and milestone_revision1.source == DataSource.ATF4_BID
        )

    @pytest.mark.parametrize("field_name", field_names)
    def test_no_errors_when_valid(self, field_name: str) -> None:
        form = ChangeMilestoneDatesForm(
            formdata=MultiDict(
                [("csrf_token", generate_csrf()), (field_name, "2"), (field_name, "1"), (field_name, "2020")]
            )
        )

        form.validate()

        assert not form.errors

    @pytest.mark.parametrize("field_name", field_names)
    def test_date_without_initial_value_is_optional(self, field_name: str) -> None:
        form = ChangeMilestoneDatesForm(formdata=MultiDict([(field_name, ""), (field_name, ""), (field_name, "")]))

        form.validate()

        assert field_name not in form.errors

    @pytest.mark.parametrize(
        "field_name, expected_error",
        [
            ("feasibility_design_completed_planned", "Enter a feasibility design completed planned date"),
            ("feasibility_design_completed_actual", "Enter a feasibility design completed actual date"),
            ("preliminary_design_completed_planned", "Enter a preliminary design completed planned date"),
            ("preliminary_design_completed_actual", "Enter a preliminary design completed actual date"),
            ("detailed_design_completed_planned", "Enter a detailed design completed planned date"),
            ("detailed_design_completed_actual", "Enter a detailed design completed actual date"),
            ("construction_started_planned", "Enter a construction started planned date"),
            ("construction_started_actual", "Enter a construction started actual date"),
            ("construction_completed_planned", "Enter a construction completed planned date"),
            ("construction_completed_actual", "Enter a construction completed actual date"),
        ],
    )
    @pytest.mark.parametrize(
        "date_",
        [
            ("", "1", "2020"),
            ("2", "", "2020"),
            ("2", "1", ""),
            ("", "", "2020"),
            ("", "1", ""),
            ("2", "", ""),
            ("", "", ""),
        ],
    )
    def test_date_with_initial_value_is_required(
        self, field_name: str, expected_error: str, date_: tuple[str, str, str]
    ) -> None:
        form = ChangeMilestoneDatesForm(data={field_name: date(2020, 1, 2)})
        form.process(formdata=MultiDict([(field_name, date_[0]), (field_name, date_[1]), (field_name, date_[2])]))

        form.validate()

        assert expected_error in form.errors[field_name]

    @pytest.mark.parametrize(
        "field_name, expected_error",
        [
            ("feasibility_design_completed_planned", "Feasibility design completed planned date must be a real date"),
            ("feasibility_design_completed_actual", "Feasibility design completed actual date must be a real date"),
            ("preliminary_design_completed_planned", "Preliminary design completed planned date must be a real date"),
            ("preliminary_design_completed_actual", "Preliminary design completed actual date must be a real date"),
            ("detailed_design_completed_planned", "Detailed design completed planned date must be a real date"),
            ("detailed_design_completed_actual", "Detailed design completed actual date must be a real date"),
            ("construction_started_planned", "Construction started planned date must be a real date"),
            ("construction_started_actual", "Construction started actual date must be a real date"),
            ("construction_completed_planned", "Construction completed planned date must be a real date"),
            ("construction_completed_actual", "Construction completed actual date must be a real date"),
        ],
    )
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
    def test_date_is_a_date(self, field_name: str, expected_error: str, date_: tuple[str, str, str]) -> None:
        form = ChangeMilestoneDatesForm(
            formdata=MultiDict([(field_name, date_[0]), (field_name, date_[1]), (field_name, date_[2])])
        )

        form.validate()

        assert expected_error in form.errors[field_name]


class TestMilestoneRevisionRepr:
    def test_from_domain(self) -> None:
        milestone_revision = MilestoneRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1, 12), datetime(2020, 2, 1, 13)),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 1, 1),
            source=DataSource.ATF4_BID,
        )

        milestone_revision_repr = MilestoneRevisionRepr.from_domain(milestone_revision)

        assert milestone_revision_repr == MilestoneRevisionRepr(
            id=1,
            effective_date_from="2020-01-01T12:00:00",
            effective_date_to="2020-02-01T13:00:00",
            milestone=MilestoneRepr.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationTypeRepr.ACTUAL,
            status_date="2020-01-01",
            source=DataSourceRepr.ATF4_BID,
        )

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
            effective_date_to="2020-02-01T13:00:00",
            milestone=MilestoneRepr.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationTypeRepr.ACTUAL,
            status_date="2020-01-01",
            source=DataSourceRepr.ATF4_BID,
        )

        milestone_revision = milestone_revision_repr.to_domain()

        assert (
            milestone_revision.id == 1
            and milestone_revision.effective == DateRange(datetime(2020, 1, 1, 12), datetime(2020, 2, 1, 13))
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
        (Milestone.FUNDING_COMPLETED, "funding completed"),
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
