from datetime import date
from decimal import Decimal

import pytest

from schemes.domain.schemes import (
    DateRange,
    ObservationType,
    OutputMeasure,
    OutputRevision,
    OutputType,
    OutputTypeMeasure,
)
from schemes.views.schemes.observations import ObservationTypeRepr
from schemes.views.schemes.outputs import (
    OutputMeasureContext,
    OutputMeasureRepr,
    OutputRevisionRepr,
    OutputTypeContext,
    OutputTypeRepr,
    SchemeOutputRowContext,
    SchemeOutputsContext,
)


class TestSchemeOutputsContext:
    def test_from_domain_orders_by_type_then_measure(self) -> None:
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

        context = SchemeOutputsContext.from_domain(output_revisions)

        assert [output.planned for output in context.outputs] == [Decimal(10), Decimal(20), Decimal(30)]

    def test_from_domain_groups_by_type_measure(self) -> None:
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

        context = SchemeOutputsContext.from_domain(output_revisions)

        assert context.outputs == [
            SchemeOutputRowContext(
                type=OutputTypeContext(name="Improvements to make an existing walking/cycle route safer"),
                measure=OutputMeasureContext(name="Miles"),
                planned=Decimal(10),
                actual=Decimal(20),
            )
        ]

    def test_from_domain_when_no_planned(self) -> None:
        output_revisions = [
            OutputRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
                value=Decimal(20),
                observation_type=ObservationType.ACTUAL,
            ),
        ]

        context = SchemeOutputsContext.from_domain(output_revisions)

        assert context.outputs[0].planned is None

    def test_from_domain_when_no_actual(self) -> None:
        output_revisions = [
            OutputRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
                value=Decimal(10),
                observation_type=ObservationType.PLANNED,
            ),
        ]

        context = SchemeOutputsContext.from_domain(output_revisions)

        assert context.outputs[0].actual is None


class TestSchemeOutputRowContext:
    @pytest.mark.parametrize(
        "planned, actual, expected_planned_not_yet_delivered",
        [(Decimal(20), Decimal(15), Decimal(5)), (Decimal(20), None, Decimal(20)), (None, Decimal(15), Decimal(-15))],
    )
    def test_planned_not_yet_delivered(
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
    def test_delivery_status(
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
    def test_from_domain(self, type_: OutputType, expected_name: str) -> None:
        context = OutputTypeContext.from_domain(type_)

        assert context == OutputTypeContext(name=expected_name)


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
    def test_from_domain(self, measure: OutputMeasure, expected_name: str) -> None:
        context = OutputMeasureContext.from_domain(measure)

        assert context == OutputMeasureContext(name=expected_name)


class TestOutputRevisionRepr:
    def test_to_domain(self) -> None:
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

    def test_to_domain_when_no_effective_date_to(self) -> None:
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
