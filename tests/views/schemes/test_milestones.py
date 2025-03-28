from datetime import date, datetime

import pytest
from flask_wtf.csrf import generate_csrf
from werkzeug.datastructures import MultiDict
from wtforms import Form, FormField, ValidationError

from schemes.domain.dates import DateRange
from schemes.domain.schemes import (
    DataSource,
    Milestone,
    MilestoneRevision,
    ObservationType,
    SchemeMilestones,
    SchemeType,
)
from schemes.views.schemes.data_sources import DataSourceRepr
from schemes.views.schemes.milestones import (
    ChangeMilestoneDatesContext,
    ChangeMilestoneDatesForm,
    MilestoneContext,
    MilestoneDateField,
    MilestoneDatesForm,
    MilestoneRepr,
    MilestoneRevisionRepr,
    SchemeMilestoneRowContext,
    SchemeMilestonesContext,
)
from schemes.views.schemes.observations import ObservationTypeRepr
from tests.builders import build_scheme


class TestSchemeMilestonesContext:
    def test_from_domain_sets_development_milestones(self) -> None:
        scheme = build_scheme(id_=0, reference="", name="", type_=SchemeType.DEVELOPMENT)

        context = SchemeMilestonesContext.from_domain(scheme)

        assert [row.milestone for row in context.milestones] == [
            MilestoneContext(name="Feasibility design completed"),
            MilestoneContext(name="Preliminary design completed"),
            MilestoneContext(name="Detailed design completed"),
        ]

    def test_from_domain_sets_construction_milestones(self) -> None:
        scheme = build_scheme(id_=0, reference="", name="", type_=SchemeType.CONSTRUCTION)

        context = SchemeMilestonesContext.from_domain(scheme)

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
        scheme = build_scheme(id_=0, reference="", name="", type_=SchemeType.CONSTRUCTION)
        scheme.milestones.update_milestones(
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

        context = SchemeMilestonesContext.from_domain(scheme)

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
        scheme = build_scheme(id_=0, reference="", name="", type_=SchemeType.CONSTRUCTION)

        context = SchemeMilestonesContext.from_domain(scheme)

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
        scheme = build_scheme(id_=1, reference="ATE00001", name="Wirral Package")
        scheme.milestones.update_milestone(
            MilestoneRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 3, 1),
                source=DataSource.ATF4_BID,
            )
        )

        context = ChangeMilestoneDatesContext.from_domain(scheme, datetime(2020, 2, 1))

        assert (
            context.id == 1
            and context.name == "Wirral Package"
            and context.form.construction_started.actual.data == date(2020, 3, 1)
        )
        with pytest.raises(ValidationError, match="Construction started actual date must not be in the future"):
            context.form.construction_started.actual.validators[0](
                context.form, context.form.construction_started.actual
            )


class TestMilestoneDateField:
    class FakeForm(Form):
        field = MilestoneDateField(required_message="This field is required.")

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
    def test_validate_is_valid_date(self, date_: tuple[str, str, str]) -> None:
        form = self.FakeForm(formdata=MultiDict([("field", date_[0]), ("field", date_[1]), ("field", date_[2])]))

        form.validate()

        assert "Not a valid date value." in form.errors["field"]

    def test_validate_without_initial_value_is_optional(self) -> None:
        form = self.FakeForm(formdata=MultiDict([("field", ""), ("field", ""), ("field", "")]))

        form.validate()

        assert "field" not in form.errors

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
    def test_validate_with_initial_value_is_required(self, date_: tuple[str, str, str]) -> None:
        form = self.FakeForm(
            data={"field": date(2020, 1, 2)},
            formdata=MultiDict([("field", date_[0]), ("field", date_[1]), ("field", date_[2])]),
        )

        form.validate()

        assert "This field is required." in form.errors["field"]


@pytest.mark.usefixtures("app")
class TestMilestoneDatesForm:
    @pytest.mark.parametrize(
        "observation_type, field_name", [(ObservationType.PLANNED, "planned"), (ObservationType.ACTUAL, "actual")]
    )
    def test_from_domain(self, observation_type: ObservationType, field_name: str) -> None:
        milestones = SchemeMilestones()
        milestones.update_milestones(
            MilestoneRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), datetime(2020, 2, 1)),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=observation_type,
                status_date=date(2020, 1, 1),
                source=DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                id_=2,
                effective=DateRange(datetime(2020, 2, 1), None),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=observation_type,
                status_date=date(2020, 2, 1),
                source=DataSource.ATF4_BID,
            ),
        )

        form = MilestoneDatesForm.from_domain(milestones, Milestone.DETAILED_DESIGN_COMPLETED, datetime.min)

        assert form[field_name].data == date(2020, 2, 1)

    def test_from_domain_when_minimal(self) -> None:
        milestones = SchemeMilestones()

        form = MilestoneDatesForm.from_domain(milestones, Milestone.DETAILED_DESIGN_COMPLETED, datetime.min)

        assert form.planned.data is None and form.actual.data is None

    @pytest.mark.parametrize(
        "field_name, observation_type", [("planned", ObservationType.PLANNED), ("actual", ObservationType.ACTUAL)]
    )
    def test_update_domain(self, field_name: str, observation_type: ObservationType) -> None:
        form_class = MilestoneDatesForm.create_class(Milestone.DETAILED_DESIGN_COMPLETED, datetime(2020, 2, 1, 13))
        form = form_class(formdata=MultiDict([(field_name, "3"), (field_name, "1"), (field_name, "2020")]))
        milestones = SchemeMilestones()
        milestones.update_milestone(
            MilestoneRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=observation_type,
                status_date=date(2020, 1, 2),
                source=DataSource.ATF4_BID,
            )
        )

        form.update_domain(milestones, datetime(2020, 2, 1, 13), Milestone.DETAILED_DESIGN_COMPLETED)

        milestone_revision1: MilestoneRevision
        milestone_revision2: MilestoneRevision
        milestone_revision1, milestone_revision2 = milestones.milestone_revisions
        assert milestone_revision1.id == 1 and milestone_revision1.effective.date_to == datetime(2020, 2, 1, 13)
        assert (
            milestone_revision2.effective == DateRange(datetime(2020, 2, 1, 13), None)
            and milestone_revision2.milestone == Milestone.DETAILED_DESIGN_COMPLETED
            and milestone_revision2.observation_type == observation_type
            and milestone_revision2.status_date == date(2020, 1, 3)
            and milestone_revision2.source == DataSource.AUTHORITY_UPDATE
        )

    @pytest.mark.parametrize(
        "field_name, observation_type", [("planned", ObservationType.PLANNED), ("actual", ObservationType.ACTUAL)]
    )
    def test_update_domain_preserves_dates_with_empty_date(
        self, field_name: str, observation_type: ObservationType
    ) -> None:
        form_class = MilestoneDatesForm.create_class(Milestone.DETAILED_DESIGN_COMPLETED, datetime(2020, 2, 1, 13))
        form = form_class(formdata=MultiDict([(field_name, ""), (field_name, ""), (field_name, "")]))
        milestones = SchemeMilestones()
        milestones.update_milestones(
            MilestoneRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1, 12), None),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=observation_type,
                status_date=date(2020, 1, 2),
                source=DataSource.ATF4_BID,
            )
        )

        form.update_domain(milestones, datetime(2020, 2, 1, 13), Milestone.DETAILED_DESIGN_COMPLETED)

        milestone_revision1: MilestoneRevision
        (milestone_revision1,) = milestones.milestone_revisions
        assert (
            milestone_revision1.id == 1
            and milestone_revision1.effective == DateRange(datetime(2020, 1, 1, 12), None)
            and milestone_revision1.milestone == Milestone.DETAILED_DESIGN_COMPLETED
            and milestone_revision1.observation_type == observation_type
            and milestone_revision1.status_date == date(2020, 1, 2)
            and milestone_revision1.source == DataSource.ATF4_BID
        )

    @pytest.mark.parametrize(
        "field_name, observation_type", [("planned", ObservationType.PLANNED), ("actual", ObservationType.ACTUAL)]
    )
    def test_update_domain_ignores_unchanged_dates(self, field_name: str, observation_type: ObservationType) -> None:
        form_class = MilestoneDatesForm.create_class(Milestone.DETAILED_DESIGN_COMPLETED, datetime(2020, 2, 1, 13))
        form = form_class(formdata=MultiDict([(field_name, "2"), (field_name, "1"), (field_name, "2020")]))
        milestones = SchemeMilestones()
        milestones.update_milestones(
            MilestoneRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1, 12), None),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=observation_type,
                status_date=date(2020, 1, 2),
                source=DataSource.ATF4_BID,
            )
        )

        form.update_domain(milestones, datetime(2020, 2, 1, 13), Milestone.DETAILED_DESIGN_COMPLETED)

        milestone_revision1: MilestoneRevision
        (milestone_revision1,) = milestones.milestone_revisions
        assert (
            milestone_revision1.id == 1
            and milestone_revision1.effective == DateRange(datetime(2020, 1, 1, 12), None)
            and milestone_revision1.milestone == Milestone.DETAILED_DESIGN_COMPLETED
            and milestone_revision1.observation_type == observation_type
            and milestone_revision1.status_date == date(2020, 1, 2)
            and milestone_revision1.source == DataSource.ATF4_BID
        )

    @pytest.mark.parametrize(
        "milestone, field_name, expected_error",
        [
            (
                Milestone.FEASIBILITY_DESIGN_COMPLETED,
                "planned",
                "Feasibility design completed planned date must be a real date",
            ),
            (
                Milestone.FEASIBILITY_DESIGN_COMPLETED,
                "actual",
                "Feasibility design completed actual date must be a real date",
            ),
            (
                Milestone.PRELIMINARY_DESIGN_COMPLETED,
                "planned",
                "Preliminary design completed planned date must be a real date",
            ),
            (
                Milestone.PRELIMINARY_DESIGN_COMPLETED,
                "actual",
                "Preliminary design completed actual date must be a real date",
            ),
            (
                Milestone.DETAILED_DESIGN_COMPLETED,
                "planned",
                "Detailed design completed planned date must be a real date",
            ),
            (
                Milestone.DETAILED_DESIGN_COMPLETED,
                "actual",
                "Detailed design completed actual date must be a real date",
            ),
            (Milestone.CONSTRUCTION_STARTED, "planned", "Construction started planned date must be a real date"),
            (Milestone.CONSTRUCTION_STARTED, "actual", "Construction started actual date must be a real date"),
            (Milestone.CONSTRUCTION_COMPLETED, "planned", "Construction completed planned date must be a real date"),
            (Milestone.CONSTRUCTION_COMPLETED, "actual", "Construction completed actual date must be a real date"),
        ],
    )
    def test_validate_is_valid_date(self, milestone: Milestone, field_name: str, expected_error: str) -> None:
        form_class = MilestoneDatesForm.create_class(milestone, datetime.min)
        form = form_class(formdata=MultiDict([(field_name, "x"), (field_name, "x"), (field_name, "x")]))

        form.validate()

        assert expected_error in form.errors[field_name]

    @pytest.mark.parametrize(
        "milestone, field_name, expected_error",
        [
            (
                Milestone.FEASIBILITY_DESIGN_COMPLETED,
                "planned",
                "Feasibility design completed planned date cannot be removed",
            ),
            (
                Milestone.FEASIBILITY_DESIGN_COMPLETED,
                "actual",
                "Feasibility design completed actual date cannot be removed",
            ),
            (
                Milestone.PRELIMINARY_DESIGN_COMPLETED,
                "planned",
                "Preliminary design completed planned date cannot be removed",
            ),
            (
                Milestone.PRELIMINARY_DESIGN_COMPLETED,
                "actual",
                "Preliminary design completed actual date cannot be removed",
            ),
            (
                Milestone.DETAILED_DESIGN_COMPLETED,
                "planned",
                "Detailed design completed planned date cannot be removed",
            ),
            (Milestone.DETAILED_DESIGN_COMPLETED, "actual", "Detailed design completed actual date cannot be removed"),
            (Milestone.CONSTRUCTION_STARTED, "planned", "Construction started planned date cannot be removed"),
            (Milestone.CONSTRUCTION_STARTED, "actual", "Construction started actual date cannot be removed"),
            (Milestone.CONSTRUCTION_COMPLETED, "planned", "Construction completed planned date cannot be removed"),
            (Milestone.CONSTRUCTION_COMPLETED, "actual", "Construction completed actual date cannot be removed"),
        ],
    )
    def test_validate_with_initial_value_is_required(
        self, milestone: Milestone, field_name: str, expected_error: str
    ) -> None:
        form_class = MilestoneDatesForm.create_class(milestone, datetime.min)
        form = form_class(
            data={field_name: date(2020, 1, 2)},
            formdata=MultiDict([(field_name, ""), (field_name, ""), (field_name, "")]),
        )

        form.validate()

        assert expected_error in form.errors[field_name]

    @pytest.mark.parametrize(
        "milestone, expected_error_message",
        [
            (
                Milestone.FEASIBILITY_DESIGN_COMPLETED,
                "Feasibility design completed actual date must not be in the future",
            ),
            (
                Milestone.PRELIMINARY_DESIGN_COMPLETED,
                "Preliminary design completed actual date must not be in the future",
            ),
            (Milestone.DETAILED_DESIGN_COMPLETED, "Detailed design completed actual date must not be in the future"),
            (Milestone.CONSTRUCTION_STARTED, "Construction started actual date must not be in the future"),
            (Milestone.CONSTRUCTION_COMPLETED, "Construction completed actual date must not be in the future"),
        ],
    )
    def test_validate_actual_date_is_not_in_the_future(self, milestone: Milestone, expected_error_message: str) -> None:
        form_class = MilestoneDatesForm.create_class(milestone, datetime(2020, 2, 1))
        form = form_class(formdata=MultiDict([("actual", "1"), ("actual", "3"), ("actual", "2020")]))

        form.validate()

        assert expected_error_message in form.errors["actual"]


@pytest.mark.usefixtures("app")
class TestChangeMilestoneDatesForm:
    field_names = [
        "feasibility_design_completed-planned",
        "feasibility_design_completed-actual",
        "preliminary_design_completed-planned",
        "preliminary_design_completed-actual",
        "detailed_design_completed-planned",
        "detailed_design_completed-actual",
        "construction_started-planned",
        "construction_started-actual",
        "construction_completed-planned",
        "construction_completed-actual",
    ]

    def test_create_class_sets_development_fields(self) -> None:
        scheme = build_scheme(id_=0, reference="", name="", type_=SchemeType.DEVELOPMENT)

        form_class = ChangeMilestoneDatesForm.create_class(scheme, datetime.min)

        form = form_class()
        fields = (field for field in form if field.name != "csrf_token")
        assert [field.name for field in fields] == [
            "feasibility_design_completed",
            "preliminary_design_completed",
            "detailed_design_completed",
        ]
        assert all(
            isinstance(field, FormField) and issubclass(field.form_class, MilestoneDatesForm) for field in fields
        )

    def test_create_class_sets_construction_fields(self) -> None:
        scheme = build_scheme(id_=0, reference="", name="", type_=SchemeType.CONSTRUCTION)

        form_class = ChangeMilestoneDatesForm.create_class(scheme, datetime.min)

        form = form_class()
        fields = (field for field in form if field.name != "csrf_token")
        assert [field.name for field in fields] == [
            "feasibility_design_completed",
            "preliminary_design_completed",
            "detailed_design_completed",
            "construction_started",
            "construction_completed",
        ]
        assert all(
            isinstance(field, FormField) and issubclass(field.form_class, MilestoneDatesForm) for field in fields
        )

    def test_create_class_sets_labels(self) -> None:
        scheme = build_scheme(id_=0, reference="", name="", type_=SchemeType.CONSTRUCTION)

        form_class = ChangeMilestoneDatesForm.create_class(scheme, datetime.min)

        form = form_class()
        assert (
            form.feasibility_design_completed.label.text == "Feasibility design completed"
            and form.preliminary_design_completed.label.text == "Preliminary design completed"
            and form.detailed_design_completed.label.text == "Detailed design completed"
            and form.construction_started.label.text == "Construction started"
            and form.construction_completed.label.text == "Construction completed"
        )

    def test_from_domain_when_development_scheme(self) -> None:
        scheme = build_scheme(id_=0, reference="", name="", type_=SchemeType.DEVELOPMENT)
        scheme.milestones.update_milestones(
            MilestoneRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                milestone=Milestone.FEASIBILITY_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 1),
                source=DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                id_=2,
                effective=DateRange(datetime(2020, 1, 1), None),
                milestone=Milestone.PRELIMINARY_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 2),
                source=DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                id_=3,
                effective=DateRange(datetime(2020, 1, 1), None),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 3),
                source=DataSource.ATF4_BID,
            ),
        )

        form = ChangeMilestoneDatesForm.from_domain(scheme, datetime.min)

        assert (
            form.feasibility_design_completed.actual.data == date(2020, 1, 1)
            and form.preliminary_design_completed.actual.data == date(2020, 1, 2)
            and form.detailed_design_completed.actual.data == date(2020, 1, 3)
        )

    def test_from_domain_when_construction_scheme(self) -> None:
        scheme = build_scheme(id_=0, reference="", name="", type_=SchemeType.CONSTRUCTION)
        scheme.milestones.update_milestones(
            MilestoneRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                milestone=Milestone.FEASIBILITY_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 1),
                source=DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                id_=2,
                effective=DateRange(datetime(2020, 1, 1), None),
                milestone=Milestone.PRELIMINARY_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 2),
                source=DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                id_=3,
                effective=DateRange(datetime(2020, 1, 1), None),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 3),
                source=DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                id_=3,
                effective=DateRange(datetime(2020, 1, 1), None),
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 4),
                source=DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                id_=3,
                effective=DateRange(datetime(2020, 1, 1), None),
                milestone=Milestone.CONSTRUCTION_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 5),
                source=DataSource.ATF4_BID,
            ),
        )

        form = ChangeMilestoneDatesForm.from_domain(scheme, datetime.min)

        assert (
            form.feasibility_design_completed.actual.data == date(2020, 1, 1)
            and form.preliminary_design_completed.actual.data == date(2020, 1, 2)
            and form.detailed_design_completed.actual.data == date(2020, 1, 3)
            and form.construction_started.actual.data == date(2020, 1, 4)
            and form.construction_completed.actual.data == date(2020, 1, 5)
        )

    def test_update_domain_when_development_scheme(self) -> None:
        scheme = build_scheme(id_=0, reference="", name="", type_=SchemeType.DEVELOPMENT)
        form_class = ChangeMilestoneDatesForm.create_class(scheme, datetime(2020, 2, 1, 13))
        form = form_class(
            feasibility_design_completed={"actual": datetime(2020, 1, 1)},
            preliminary_design_completed={"actual": datetime(2020, 1, 2)},
            detailed_design_completed={"actual": datetime(2020, 1, 3)},
        )

        form.update_domain(scheme, datetime(2020, 2, 1, 13))

        assert all(
            milestone_revision.effective.date_from == datetime(2020, 2, 1, 13)
            for milestone_revision in scheme.milestones.milestone_revisions
        )
        assert [milestone_revision.status_date for milestone_revision in scheme.milestones.milestone_revisions] == [
            datetime(2020, 1, 1),
            datetime(2020, 1, 2),
            datetime(2020, 1, 3),
        ]

    def test_update_domain_when_construction_scheme(self) -> None:
        scheme = build_scheme(id_=0, reference="", name="", type_=SchemeType.CONSTRUCTION)
        form_class = ChangeMilestoneDatesForm.create_class(scheme, datetime(2020, 2, 1, 13))
        form = form_class(
            feasibility_design_completed={"actual": datetime(2020, 1, 1)},
            preliminary_design_completed={"actual": datetime(2020, 1, 2)},
            detailed_design_completed={"actual": datetime(2020, 1, 3)},
            construction_started={"actual": datetime(2020, 1, 4)},
            construction_completed={"actual": datetime(2020, 1, 5)},
        )

        form.update_domain(scheme, datetime(2020, 2, 1, 13))

        assert all(
            milestone_revision.effective.date_from == datetime(2020, 2, 1, 13)
            for milestone_revision in scheme.milestones.milestone_revisions
        )
        assert [milestone_revision.status_date for milestone_revision in scheme.milestones.milestone_revisions] == [
            datetime(2020, 1, 1),
            datetime(2020, 1, 2),
            datetime(2020, 1, 3),
            datetime(2020, 1, 4),
            datetime(2020, 1, 5),
        ]

    def test_cannot_update_domain_with_construction_milestones_when_development_scheme(self) -> None:
        construction_scheme = build_scheme(id_=0, reference="", name="", type_=SchemeType.CONSTRUCTION)
        form_class = ChangeMilestoneDatesForm.create_class(construction_scheme, datetime(2020, 2, 1, 13))
        form = form_class(
            construction_started={"actual": datetime(2020, 1, 4)},
            construction_completed={"actual": datetime(2020, 1, 5)},
        )
        development_scheme = build_scheme(id_=0, reference="", name="", type_=SchemeType.DEVELOPMENT)

        form.update_domain(development_scheme, datetime(2020, 2, 1, 13))

        assert not development_scheme.milestones.milestone_revisions

    @pytest.mark.parametrize("field_name", field_names)
    def test_validate_when_valid(self, field_name: str) -> None:
        scheme = build_scheme(id_=0, reference="", name="", type_=SchemeType.CONSTRUCTION)
        form_class = ChangeMilestoneDatesForm.create_class(scheme, datetime(2020, 2, 1))
        form = form_class(
            formdata=MultiDict(
                [("csrf_token", generate_csrf()), (field_name, "2"), (field_name, "1"), (field_name, "2020")]
            )
        )

        form.validate()

        assert not form.errors


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
