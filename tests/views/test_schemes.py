from datetime import date
from decimal import Decimal

import pytest

from schemes.domain.authorities import Authority
from schemes.domain.schemes import (
    DataSource,
    DateRange,
    FinancialRevision,
    FinancialType,
    FundingProgramme,
    Milestone,
    MilestoneRevision,
    ObservationType,
    OutputMeasure,
    OutputRevision,
    OutputType,
    OutputTypeMeasure,
    Scheme,
    SchemeFunding,
    SchemeType,
)
from schemes.views.schemes import (
    DataSourceRepr,
    FinancialRevisionRepr,
    FinancialTypeRepr,
    FundingProgrammeContext,
    FundingProgrammeRepr,
    MilestoneContext,
    MilestoneRepr,
    MilestoneRevisionRepr,
    ObservationTypeRepr,
    OutputMeasureContext,
    OutputMeasureRepr,
    OutputRevisionRepr,
    OutputTypeContext,
    OutputTypeRepr,
    SchemeContext,
    SchemeFundingContext,
    SchemeMilestoneRowContext,
    SchemeMilestonesContext,
    SchemeOutputRowContext,
    SchemeOutputsContext,
    SchemeOverviewContext,
    SchemeRepr,
    SchemeRowContext,
    SchemesContext,
    SchemeTypeContext,
    SchemeTypeRepr,
)


class TestSchemesContext:
    def test_create_from_domain(self) -> None:
        authority = Authority(id_=1, name="Liverpool City Region Combined Authority")
        schemes = [
            Scheme(id_=1, name="Wirral Package", authority_id=1),
            Scheme(id_=2, name="School Streets", authority_id=1),
        ]

        context = SchemesContext.for_domain(authority, schemes)

        assert (
            context.authority_name == "Liverpool City Region Combined Authority"
            and context.schemes[0].reference == "ATE00001"
            and context.schemes[1].reference == "ATE00002"
        )


class TestSchemesRowContext:
    def test_create_from_domain(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme.funding_programme = FundingProgramme.ATF4

        context = SchemeRowContext.for_domain(scheme)

        assert context == SchemeRowContext(
            id=1,
            reference="ATE00001",
            funding_programme=FundingProgrammeContext(name="ATF4"),
            name="Wirral Package",
        )


class TestSchemeContext:
    def test_create_from_domain(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.funding.update_financial(
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal(100000),
                source=DataSource.ATF4_BID,
            )
        )
        scheme.milestones.update_milestones(
            MilestoneRevision(
                effective=DateRange(date(2020, 1, 1), date(2020, 1, 31)),
                milestone=Milestone.PUBLIC_CONSULTATION_COMPLETED,
                observation_type=ObservationType.PLANNED,
                status_date=date(2020, 1, 1),
            ),
            MilestoneRevision(
                effective=DateRange(date(2020, 2, 1), None),
                milestone=Milestone.PUBLIC_CONSULTATION_COMPLETED,
                observation_type=ObservationType.PLANNED,
                status_date=date(2020, 2, 1),
            ),
        )
        scheme.outputs.update_outputs(
            OutputRevision(
                effective=DateRange(date(2020, 1, 1), date(2020, 1, 31)),
                type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
                value=Decimal(10),
                observation_type=ObservationType.PLANNED,
            ),
            OutputRevision(
                effective=DateRange(date(2020, 2, 1), None),
                type_measure=OutputTypeMeasure.RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY_NUMBER_OF_PARKING_SPACES,
                value=Decimal(20),
                observation_type=ObservationType.PLANNED,
            ),
        )

        context = SchemeContext.for_domain(scheme)

        assert (
            context.name == "Wirral Package"
            and context.overview.reference == "ATE00001"
            and context.funding.funding_allocation == Decimal(100000)
            and context.milestones.milestones[0].planned == date(2020, 2, 1)
            and context.outputs.outputs[0].planned == Decimal(20)
        )


class TestSchemeOverviewContext:
    def test_reference(self) -> None:
        scheme = Scheme(id_=1, name="", authority_id=0)

        context = SchemeOverviewContext.for_domain(scheme)

        assert context.reference == "ATE00001"

    def test_set_type(self) -> None:
        scheme = Scheme(id_=0, name="", authority_id=0)
        scheme.type = SchemeType.CONSTRUCTION

        context = SchemeOverviewContext.for_domain(scheme)

        assert context.type == SchemeTypeContext(name="Construction")

    def test_set_funding_programme(self) -> None:
        scheme = Scheme(id_=0, name="", authority_id=0)
        scheme.funding_programme = FundingProgramme.ATF4

        context = SchemeOverviewContext.for_domain(scheme)

        assert context.funding_programme == FundingProgrammeContext(name="ATF4")

    def test_set_current_milestone(self) -> None:
        scheme = Scheme(id_=0, name="", authority_id=0)
        scheme.milestones.update_milestone(
            MilestoneRevision(
                effective=DateRange(date(2020, 1, 1), None),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 1),
            )
        )

        context = SchemeOverviewContext.for_domain(scheme)

        assert context.current_milestone == MilestoneContext(name="Detailed design completed")

    def test_set_current_milestone_when_no_revisions(self) -> None:
        scheme = Scheme(id_=0, name="", authority_id=0)

        context = SchemeOverviewContext.for_domain(scheme)

        assert context.current_milestone == MilestoneContext(name=None)


class TestSchemeTypeContext:
    @pytest.mark.parametrize(
        "type_, expected_name",
        [(SchemeType.DEVELOPMENT, "Development"), (SchemeType.CONSTRUCTION, "Construction"), (None, None)],
    )
    def test_set_name(self, type_: SchemeType | None, expected_name: str | None) -> None:
        context = SchemeTypeContext.for_domain(type_)

        assert context.name == expected_name


class TestFundingProgrammeContext:
    @pytest.mark.parametrize(
        "funding_programme, expected_name",
        [
            (FundingProgramme.ATF2, "ATF2"),
            (FundingProgramme.ATF3, "ATF3"),
            (FundingProgramme.ATF4, "ATF4"),
            (FundingProgramme.ATF4E, "ATF4e"),
            (FundingProgramme.ATF5, "ATF5"),
            (FundingProgramme.MRN, "MRN"),
            (FundingProgramme.LUF, "LUF"),
            (FundingProgramme.CRSTS, "CRSTS"),
            (None, None),
        ],
    )
    def test_set_name(self, funding_programme: FundingProgramme | None, expected_name: str | None) -> None:
        context = FundingProgrammeContext.for_domain(funding_programme)

        assert context.name == expected_name


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
    def test_set_name(self, milestone: Milestone | None, expected_name: str | None) -> None:
        context = MilestoneContext.for_domain(milestone)

        assert context.name == expected_name


class TestSchemeFundingContext:
    def test_set_funding_allocation(self) -> None:
        funding = SchemeFunding()
        funding.update_financial(
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal(100000),
                source=DataSource.ATF4_BID,
            )
        )

        context = SchemeFundingContext.for_domain(funding)

        assert context.funding_allocation == Decimal(100000)

    def test_set_spend_to_date(self) -> None:
        funding = SchemeFunding()
        funding.update_financial(
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.SPENT_TO_DATE,
                amount=Decimal(50000),
                source=DataSource.ATF4_BID,
            )
        )

        context = SchemeFundingContext.for_domain(funding)

        assert context.spend_to_date == Decimal(50000)

    def test_set_change_control_adjustment(self) -> None:
        funding = SchemeFunding()
        funding.update_financial(
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal(10000),
                source=DataSource.CHANGE_CONTROL,
            )
        )

        context = SchemeFundingContext.for_domain(funding)

        assert context.change_control_adjustment == Decimal(10000)

    def test_set_allocation_still_to_spend(self) -> None:
        funding = SchemeFunding()
        funding.update_financials(
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal(110000),
                source=DataSource.ATF4_BID,
            ),
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.SPENT_TO_DATE,
                amount=Decimal(50000),
                source=DataSource.ATF4_BID,
            ),
        )

        context = SchemeFundingContext.for_domain(funding)

        assert context.allocation_still_to_spend == Decimal(60000)


class TestSchemeMilestonesContext:
    def test_create_from_domain_returns_correct_milestones(self) -> None:
        context = SchemeMilestonesContext.for_domain([])

        assert [row.milestone for row in context.milestones] == [
            MilestoneContext(name="Public consultation completed"),
            MilestoneContext(name="Feasibility design completed"),
            MilestoneContext(name="Preliminary design completed"),
            MilestoneContext(name="Detailed design completed"),
            MilestoneContext(name="Construction started"),
            MilestoneContext(name="Construction completed"),
        ]

    @pytest.mark.parametrize(
        "milestone, expected_milestone_name",
        [
            (Milestone.PUBLIC_CONSULTATION_COMPLETED, "Public consultation completed"),
            (Milestone.FEASIBILITY_DESIGN_COMPLETED, "Feasibility design completed"),
            (Milestone.PRELIMINARY_DESIGN_COMPLETED, "Preliminary design completed"),
            (Milestone.DETAILED_DESIGN_COMPLETED, "Detailed design completed"),
            (Milestone.CONSTRUCTION_STARTED, "Construction started"),
            (Milestone.CONSTRUCTION_COMPLETED, "Construction completed"),
        ],
    )
    def test_create_from_domain_returns_milestone_dates(
        self, milestone: Milestone, expected_milestone_name: str
    ) -> None:
        milestone_revisions = [
            MilestoneRevision(
                effective=DateRange(date(2020, 1, 1), None),
                milestone=milestone,
                observation_type=ObservationType.PLANNED,
                status_date=date(2020, 2, 1),
            ),
            MilestoneRevision(
                effective=DateRange(date(2020, 1, 1), None),
                milestone=milestone,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 3, 1),
            ),
        ]

        context = SchemeMilestonesContext.for_domain(milestone_revisions)

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
            "Public consultation completed",
            "Feasibility design completed",
            "Preliminary design completed",
            "Detailed design completed",
            "Construction started",
            "Construction completed",
        ],
    )
    def test_create_from_domain_returns_milestone_dates_when_no_revisions(self, expected_milestone_name: str) -> None:
        context = SchemeMilestonesContext.for_domain([])

        assert (
            SchemeMilestoneRowContext(
                milestone=MilestoneContext(name=expected_milestone_name), planned=None, actual=None
            )
            in context.milestones
        )


class TestSchemeOutputsContext:
    def test_create_from_domain_is_ordered_by_type_then_measure(self) -> None:
        output_revisions = [
            OutputRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type_measure=OutputTypeMeasure.RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY_MILES,
                value=Decimal(30),
                observation_type=ObservationType.PLANNED,
            ),
            OutputRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_NUMBER_OF_JUNCTIONS,
                value=Decimal(20),
                observation_type=ObservationType.PLANNED,
            ),
            OutputRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
                value=Decimal(10),
                observation_type=ObservationType.PLANNED,
            ),
        ]

        context = SchemeOutputsContext.for_domain(output_revisions)

        assert [output.planned for output in context.outputs] == [Decimal(10), Decimal(20), Decimal(30)]

    def test_create_from_domain_groups_by_type_measure(self) -> None:
        output_revisions = [
            OutputRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
                value=Decimal(10),
                observation_type=ObservationType.PLANNED,
            ),
            OutputRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
                value=Decimal(20),
                observation_type=ObservationType.ACTUAL,
            ),
        ]

        context = SchemeOutputsContext.for_domain(output_revisions)

        assert context.outputs == [
            SchemeOutputRowContext(
                type=OutputTypeContext(name="Improvements to make an existing walking/cycle route safer"),
                measure=OutputMeasureContext(name="Miles"),
                planned=Decimal(10),
                actual=Decimal(20),
            )
        ]

    def test_create_from_domain_when_no_planned(self) -> None:
        output_revisions = [
            OutputRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
                value=Decimal(20),
                observation_type=ObservationType.ACTUAL,
            ),
        ]

        context = SchemeOutputsContext.for_domain(output_revisions)

        assert context.outputs[0].planned is None

    def test_create_from_domain_when_no_actual(self) -> None:
        output_revisions = [
            OutputRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
                value=Decimal(10),
                observation_type=ObservationType.PLANNED,
            ),
        ]

        context = SchemeOutputsContext.for_domain(output_revisions)

        assert context.outputs[0].actual is None


class TestSchemeOutputRowContext:
    @pytest.mark.parametrize(
        "planned, actual, expected_planned_not_yet_delivered",
        [(Decimal(20), Decimal(15), Decimal(5)), (Decimal(20), None, Decimal(20)), (None, Decimal(15), Decimal(-15))],
    )
    def test_set_planned_not_yet_delivered(
        self, planned: Decimal | None, actual: Decimal | None, expected_planned_not_yet_delivered: Decimal | None
    ) -> None:
        context = SchemeOutputRowContext(
            type=OutputTypeContext(name="Improvements to make an existing walking/cycle route safer"),
            measure=OutputMeasureContext(name="miles"),
            planned=planned,
            actual=actual,
        )

        assert context.planned_not_yet_delivered == expected_planned_not_yet_delivered

    @pytest.mark.parametrize(
        "planned, actual, expected_delivery_status",
        [
            (None, Decimal(0), "No outputs recorded"),
            (Decimal(0), None, "No outputs recorded"),
            (Decimal(10), None, "Not started"),
            (Decimal(10), Decimal(0), "Not started"),
            (Decimal(10), Decimal(5), "In progress"),
            (Decimal(10), Decimal(10), "Complete"),
            (Decimal(10), Decimal(20), "More outputs than planned"),
        ],
    )
    def test_set_delivery_status(
        self, planned: Decimal | None, actual: Decimal | None, expected_delivery_status: str
    ) -> None:
        context = SchemeOutputRowContext(
            type=OutputTypeContext(name="Improvements to make an existing walking/cycle route safer"),
            measure=OutputMeasureContext(name="miles"),
            planned=planned,
            actual=actual,
        )

        assert context.delivery_status == expected_delivery_status


class TestOutputTypeContext:
    @pytest.mark.parametrize(
        "type_, expected_name",
        [
            (OutputType.NEW_SEGREGATED_CYCLING_FACILITY, "New segregated cycling facility"),
            (OutputType.NEW_TEMPORARY_SEGREGATED_CYCLING_FACILITY, "New temporary segregated cycling facility"),
            (OutputType.NEW_JUNCTION_TREATMENT, "New junction treatment"),
            (OutputType.NEW_PERMANENT_FOOTWAY, "New permanent footway"),
            (OutputType.NEW_TEMPORARY_FOOTWAY, "New temporary footway"),
            (OutputType.NEW_SHARED_USE_FACILITIES, "New shared use (walking and cycling) facilities"),
            (OutputType.NEW_SHARED_USE_FACILITIES_WHEELING, "New shared use (walking, wheeling & cycling) facilities"),
            (OutputType.IMPROVEMENTS_TO_EXISTING_ROUTE, "Improvements to make an existing walking/cycle route safer"),
            (
                OutputType.AREA_WIDE_TRAFFIC_MANAGEMENT,
                "Area-wide traffic management (including by TROs (both permanent and experimental))",
            ),
            (
                OutputType.BUS_PRIORITY_MEASURES,
                "Bus priority measures that also enable active travel (for example, bus gates)",
            ),
            (OutputType.SECURE_CYCLE_PARKING, "Provision of secure cycle parking facilities"),
            (OutputType.NEW_ROAD_CROSSINGS, "New road crossings"),
            (
                OutputType.RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY,
                "Restriction or reduction of car parking availability",
            ),
            (OutputType.SCHOOL_STREETS, "School streets"),
            (
                OutputType.UPGRADES_TO_EXISTING_FACILITIES,
                "Upgrades to existing facilities (e.g. surfacing, signage, signals)",
            ),
            (OutputType.E_SCOOTER_TRIALS, "E-scooter trials"),
            (OutputType.PARK_AND_CYCLE_STRIDE_FACILITIES, "Park and cycle/stride facilities"),
            (OutputType.TRAFFIC_CALMING, "Traffic calming (e.g. lane closures, reducing speed limits)"),
            (OutputType.WIDENING_EXISTING_FOOTWAY, "Widening existing footway"),
            (OutputType.OTHER_INTERVENTIONS, "Other interventions"),
        ],
    )
    def test_set_name(self, type_: OutputType, expected_name: str) -> None:
        context = OutputTypeContext.for_domain(type_)

        assert context.name == expected_name


class TestOutputMeasureContext:
    @pytest.mark.parametrize(
        "measure, expected_name",
        [
            (OutputMeasure.MILES, "Miles"),
            (OutputMeasure.NUMBER_OF_JUNCTIONS, "Number of junctions"),
            (OutputMeasure.SIZE_OF_AREA, "Size of area"),
            (OutputMeasure.NUMBER_OF_PARKING_SPACES, "Number of parking spaces"),
            (OutputMeasure.NUMBER_OF_CROSSINGS, "Number of crossings"),
            (OutputMeasure.NUMBER_OF_SCHOOL_STREETS, "Number of school streets"),
            (OutputMeasure.NUMBER_OF_TRIALS, "Number of trials"),
            (OutputMeasure.NUMBER_OF_BUS_GATES, "Number of bus gates"),
            (OutputMeasure.NUMBER_OF_UPGRADES, "Number of upgrades"),
            (OutputMeasure.NUMBER_OF_CHILDREN_AFFECTED, "Number of children affected"),
            (OutputMeasure.NUMBER_OF_MEASURES_PLANNED, "Number of measures planned"),
        ],
    )
    def test_set_name(self, measure: OutputMeasure, expected_name: str) -> None:
        context = OutputMeasureContext.for_domain(measure)

        assert context.name == expected_name


class TestSchemeRepr:
    def test_create_domain(self) -> None:
        scheme_repr = SchemeRepr(
            id=1, name="Wirral Package", type=SchemeTypeRepr.CONSTRUCTION, funding_programme=FundingProgrammeRepr.ATF4
        )

        scheme = scheme_repr.to_domain(2)

        assert (
            scheme.id == 1
            and scheme.name == "Wirral Package"
            and scheme.authority_id == 2
            and scheme.type == SchemeType.CONSTRUCTION
            and scheme.funding_programme == FundingProgramme.ATF4
        )

    def test_create_minimal_domain(self) -> None:
        scheme_repr = SchemeRepr(id=1, name="Wirral Package")

        scheme = scheme_repr.to_domain(2)

        assert (
            scheme.id == 1
            and scheme.name == "Wirral Package"
            and scheme.authority_id == 2
            and scheme.type is None
            and scheme.funding_programme is None
        )

    def test_set_financial_revisions(self) -> None:
        scheme_repr = SchemeRepr(
            id=0,
            name="",
            financial_revisions=[
                FinancialRevisionRepr(
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    type=FinancialTypeRepr.FUNDING_ALLOCATION,
                    amount="100000",
                    source=DataSourceRepr.ATF4_BID,
                ),
                FinancialRevisionRepr(
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    type=FinancialTypeRepr.EXPECTED_COST,
                    amount="200000",
                    source=DataSourceRepr.PULSE_6,
                ),
            ],
        )

        scheme = scheme_repr.to_domain(0)

        assert scheme.funding.financial_revisions == [
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal(100000),
                source=DataSource.ATF4_BID,
            ),
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.EXPECTED_COST,
                amount=Decimal(200000),
                source=DataSource.PULSE_6,
            ),
        ]

    def test_set_milestone_revisions(self) -> None:
        scheme_repr = SchemeRepr(
            id=0,
            name="",
            milestone_revisions=[
                MilestoneRevisionRepr(
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    milestone=MilestoneRepr.DETAILED_DESIGN_COMPLETED,
                    observation_type=ObservationTypeRepr.ACTUAL,
                    status_date="2020-01-01",
                ),
                MilestoneRevisionRepr(
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    milestone=MilestoneRepr.CONSTRUCTION_STARTED,
                    observation_type=ObservationTypeRepr.ACTUAL,
                    status_date="2020-02-01",
                ),
            ],
        )

        scheme = scheme_repr.to_domain(0)

        assert scheme.milestones.milestone_revisions == [
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
                status_date=date(2020, 2, 1),
            ),
        ]

    def test_set_output_revisions(self) -> None:
        scheme_repr = SchemeRepr(
            id=0,
            name="",
            output_revisions=[
                OutputRevisionRepr(
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    type=OutputTypeRepr.IMPROVEMENTS_TO_EXISTING_ROUTE,
                    measure=OutputMeasureRepr.MILES,
                    value="10",
                    observation_type=ObservationTypeRepr.ACTUAL,
                ),
                OutputRevisionRepr(
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    type=OutputTypeRepr.IMPROVEMENTS_TO_EXISTING_ROUTE,
                    measure=OutputMeasureRepr.NUMBER_OF_JUNCTIONS,
                    value="3",
                    observation_type=ObservationTypeRepr.ACTUAL,
                ),
            ],
        )

        scheme = scheme_repr.to_domain(0)

        assert scheme.outputs.output_revisions == [
            OutputRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
                value=Decimal(10),
                observation_type=ObservationType.ACTUAL,
            ),
            OutputRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_NUMBER_OF_JUNCTIONS,
                value=Decimal(3),
                observation_type=ObservationType.ACTUAL,
            ),
        ]


class TestSchemeTypeRepr:
    @pytest.mark.parametrize(
        "type_, expected_type",
        [("development", SchemeType.DEVELOPMENT), ("construction", SchemeType.CONSTRUCTION)],
    )
    def test_to_domain(self, type_: str, expected_type: SchemeType) -> None:
        assert SchemeTypeRepr(type_).to_domain() == expected_type


class TestFundingProgrammeRepr:
    @pytest.mark.parametrize(
        "funding_programme, expected_funding_programme",
        [
            ("ATF2", FundingProgramme.ATF2),
            ("ATF3", FundingProgramme.ATF3),
            ("ATF4", FundingProgramme.ATF4),
            ("ATF4e", FundingProgramme.ATF4E),
            ("ATF5", FundingProgramme.ATF5),
            ("MRN", FundingProgramme.MRN),
            ("LUF", FundingProgramme.LUF),
            ("CRSTS", FundingProgramme.CRSTS),
        ],
    )
    def test_to_domain(self, funding_programme: str, expected_funding_programme: FundingProgramme) -> None:
        assert FundingProgrammeRepr(funding_programme).to_domain() == expected_funding_programme


class TestFinancialRevisionRepr:
    def test_create_domain(self) -> None:
        financial_revision_repr = FinancialRevisionRepr(
            effective_date_from="2020-01-01",
            effective_date_to="2020-01-31",
            type=FinancialTypeRepr.FUNDING_ALLOCATION,
            amount="100000",
            source=DataSourceRepr.ATF4_BID,
        )

        financial_revision = financial_revision_repr.to_domain()

        assert financial_revision == FinancialRevision(
            effective=DateRange(date(2020, 1, 1), date(2020, 1, 31)),
            type=FinancialType.FUNDING_ALLOCATION,
            amount=Decimal(100000),
            source=DataSource.ATF4_BID,
        )

    def test_set_effective_date_to_when_missing(self) -> None:
        financial_revision_repr = FinancialRevisionRepr(
            effective_date_from="2020-01-01",
            effective_date_to=None,
            type=FinancialTypeRepr.FUNDING_ALLOCATION,
            amount="100000",
            source=DataSourceRepr.ATF4_BID,
        )

        financial_revision = financial_revision_repr.to_domain()

        assert financial_revision.effective.date_to is None


class TestFinancialTypeRepr:
    @pytest.mark.parametrize(
        "financial_type, expected_financial_type",
        [
            ("expected cost", FinancialType.EXPECTED_COST),
            ("actual cost", FinancialType.ACTUAL_COST),
            ("funding allocation", FinancialType.FUNDING_ALLOCATION),
            ("spent to date", FinancialType.SPENT_TO_DATE),
            ("funding request", FinancialType.FUNDING_REQUEST),
        ],
    )
    def test_to_domain(self, financial_type: str, expected_financial_type: FinancialType) -> None:
        assert FinancialTypeRepr(financial_type).to_domain() == expected_financial_type


class TestDataSourceRepr:
    @pytest.mark.parametrize(
        "data_source, expected_data_source",
        [
            ("Pulse 5", DataSource.PULSE_5),
            ("Pulse 6", DataSource.PULSE_6),
            ("ATF4 Bid", DataSource.ATF4_BID),
            ("ATF3 Bid", DataSource.ATF3_BID),
            ("Inspectorate review", DataSource.INSPECTORATE_REVIEW),
            ("Regional Engagement Manager review", DataSource.REGIONAL_ENGAGEMENT_MANAGER_REVIEW),
            ("ATE published data", DataSource.ATE_PUBLISHED_DATA),
            ("change control", DataSource.CHANGE_CONTROL),
            ("ATF4e Bid", DataSource.ATF4E_BID),
            ("Pulse 2023/24 Q2", DataSource.PULSE_2023_24_Q2),
            ("Initial Scheme List", DataSource.INITIAL_SCHEME_LIST),
        ],
    )
    def test_to_domain(self, data_source: str, expected_data_source: DataSource) -> None:
        assert DataSourceRepr(data_source).to_domain() == expected_data_source


class TestMilestoneRevisionRepr:
    def test_create_domain(self) -> None:
        milestone_revision_repr = MilestoneRevisionRepr(
            effective_date_from="2020-01-01",
            effective_date_to="2020-01-31",
            milestone=MilestoneRepr.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationTypeRepr.ACTUAL,
            status_date="2020-01-01",
        )

        milestone_revision = milestone_revision_repr.to_domain()

        assert milestone_revision == MilestoneRevision(
            effective=DateRange(date(2020, 1, 1), date(2020, 1, 31)),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 1, 1),
        )

    def test_set_effective_date_to_when_missing(self) -> None:
        milestone_revision_repr = MilestoneRevisionRepr(
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


class TestObservationTypeRepr:
    @pytest.mark.parametrize(
        "observation_type, expected_observation_type",
        [
            ("Planned", ObservationType.PLANNED),
            ("Actual", ObservationType.ACTUAL),
        ],
    )
    def test_to_domain(self, observation_type: str, expected_observation_type: ObservationType) -> None:
        assert ObservationTypeRepr(observation_type).to_domain() == expected_observation_type


class TestOutputRevisionRepr:
    def test_create_domain(self) -> None:
        output_revision_repr = OutputRevisionRepr(
            effective_date_from="2020-01-01",
            effective_date_to="2020-01-31",
            type=OutputTypeRepr.IMPROVEMENTS_TO_EXISTING_ROUTE,
            measure=OutputMeasureRepr.MILES,
            value="10",
            observation_type=ObservationTypeRepr.ACTUAL,
        )

        output_revision = output_revision_repr.to_domain()

        assert output_revision == OutputRevision(
            effective=DateRange(date(2020, 1, 1), date(2020, 1, 31)),
            type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
            value=Decimal(10),
            observation_type=ObservationType.ACTUAL,
        )

    def test_set_effective_date_to_when_missing(self) -> None:
        output_revision_repr = OutputRevisionRepr(
            effective_date_from="2020-01-01",
            effective_date_to=None,
            type=OutputTypeRepr.IMPROVEMENTS_TO_EXISTING_ROUTE,
            measure=OutputMeasureRepr.MILES,
            value="10",
            observation_type=ObservationTypeRepr.ACTUAL,
        )

        output_revision = output_revision_repr.to_domain()

        assert output_revision.effective.date_to is None


class TestOutputTypeRepr:
    @pytest.mark.parametrize(
        "type_, expected_type",
        [
            ("New segregated cycling facility", OutputType.NEW_SEGREGATED_CYCLING_FACILITY),
            ("New temporary segregated cycling facility", OutputType.NEW_TEMPORARY_SEGREGATED_CYCLING_FACILITY),
            ("New junction treatment", OutputType.NEW_JUNCTION_TREATMENT),
            ("New permanent footway", OutputType.NEW_PERMANENT_FOOTWAY),
            ("New temporary footway", OutputType.NEW_TEMPORARY_FOOTWAY),
            ("New shared use (walking and cycling) facilities", OutputType.NEW_SHARED_USE_FACILITIES),
            ("New shared use (walking, wheeling & cycling) facilities", OutputType.NEW_SHARED_USE_FACILITIES_WHEELING),
            ("Improvements to make an existing walking/cycle route safer", OutputType.IMPROVEMENTS_TO_EXISTING_ROUTE),
            (
                "Area-wide traffic management (including by TROs (both permanent and experimental))",
                OutputType.AREA_WIDE_TRAFFIC_MANAGEMENT,
            ),
            (
                "Bus priority measures that also enable active travel (for example, bus gates)",
                OutputType.BUS_PRIORITY_MEASURES,
            ),
            ("Provision of secure cycle parking facilities", OutputType.SECURE_CYCLE_PARKING),
            ("New road crossings", OutputType.NEW_ROAD_CROSSINGS),
            (
                "Restriction or reduction of car parking availability",
                OutputType.RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY,
            ),
            ("School streets", OutputType.SCHOOL_STREETS),
            (
                "Upgrades to existing facilities (e.g. surfacing, signage, signals)",
                OutputType.UPGRADES_TO_EXISTING_FACILITIES,
            ),
            ("E-scooter trials", OutputType.E_SCOOTER_TRIALS),
            ("Park and cycle/stride facilities", OutputType.PARK_AND_CYCLE_STRIDE_FACILITIES),
            ("Traffic calming (e.g. lane closures, reducing speed limits)", OutputType.TRAFFIC_CALMING),
            ("Widening existing footway", OutputType.WIDENING_EXISTING_FOOTWAY),
            ("Other interventions", OutputType.OTHER_INTERVENTIONS),
        ],
    )
    def test_to_domain(self, type_: str, expected_type: OutputType) -> None:
        assert OutputTypeRepr(type_).to_domain() == expected_type


class TestOutputMeasureRepr:
    @pytest.mark.parametrize(
        "measure, expected_measure",
        [
            ("miles", OutputMeasure.MILES),
            ("number of junctions", OutputMeasure.NUMBER_OF_JUNCTIONS),
            ("size of area", OutputMeasure.SIZE_OF_AREA),
            ("number of parking spaces", OutputMeasure.NUMBER_OF_PARKING_SPACES),
            ("number of crossings", OutputMeasure.NUMBER_OF_CROSSINGS),
            ("number of school streets", OutputMeasure.NUMBER_OF_SCHOOL_STREETS),
            ("number of trials", OutputMeasure.NUMBER_OF_TRIALS),
            ("number of bus gates", OutputMeasure.NUMBER_OF_BUS_GATES),
            ("number of upgrades", OutputMeasure.NUMBER_OF_UPGRADES),
            ("number of children affected", OutputMeasure.NUMBER_OF_CHILDREN_AFFECTED),
            ("number of measures planned", OutputMeasure.NUMBER_OF_MEASURES_PLANNED),
        ],
    )
    def test_to_domain(self, measure: str, expected_measure: OutputMeasure) -> None:
        assert OutputMeasureRepr(measure).to_domain() == expected_measure
