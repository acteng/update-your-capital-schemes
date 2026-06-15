from datetime import datetime
from decimal import Decimal

import pytest

from schemes.domain.dates import DateRange
from schemes.domain.schemes.observations import ObservationType
from schemes.domain.schemes.outputs import OutputMeasure, OutputRevision, OutputType, OutputTypeMeasure
from schemes.views.schemes.outputs import (
    OutputMeasureContext,
    OutputTypeContext,
    SchemeOutputRowContext,
    SchemeOutputsContext,
)


class TestSchemeOutputsContext:
    def test_from_domain_orders_by_type_then_measure(self) -> None:
        output_revisions = [
            OutputRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_measure=OutputTypeMeasure.RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY_MILES,
                value=Decimal(30),
                observation_type=ObservationType.PLANNED,
            ),
            OutputRevision(
                id_=2,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_NUMBER_OF_JUNCTIONS,
                value=Decimal(20),
                observation_type=ObservationType.PLANNED,
            ),
            OutputRevision(
                id_=3,
                effective=DateRange(datetime(2020, 1, 1), None),
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
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
                value=Decimal(10),
                observation_type=ObservationType.PLANNED,
            )
        ]

        context = SchemeOutputsContext.from_domain(output_revisions)

        assert context.outputs == [
            SchemeOutputRowContext(
                type=OutputTypeContext(name="Improvements to make an existing walking/cycle route safer"),
                measure=OutputMeasureContext(name="Miles"),
                planned=Decimal(10),
            )
        ]

    def test_from_domain_when_no_planned(self) -> None:
        output_revisions = [
            OutputRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
                value=Decimal(20),
                observation_type=ObservationType.ACTUAL,
            ),
        ]

        context = SchemeOutputsContext.from_domain(output_revisions)

        assert context.outputs[0].planned is None


class TestOutputTypeContext:
    @pytest.mark.parametrize(
        "type_, expected_name",
        [
            (OutputType.NEW_SEGREGATED_CYCLING_FACILITY, "New segregated cycling facility"),
            (OutputType.NEW_TEMPORARY_SEGREGATED_CYCLING_FACILITY, "New temporary segregated cycling facility"),
            (OutputType.NEW_JUNCTION_TREATMENT, "New junction treatment"),
            (OutputType.NEW_PERMANENT_FOOTWAY, "New permanent footway"),
            (OutputType.NEW_TEMPORARY_FOOTWAY, "New temporary footway"),
            (
                OutputType.NEW_SHARED_USE_WALKING_AND_CYCLING_FACILITIES,
                "New shared use (walking and cycling) facilities",
            ),
            (
                OutputType.NEW_SHARED_USE_WALKING_WHEELING_AND_CYCLING_FACILITIES,
                "New shared use (walking, wheeling & cycling) facilities",
            ),
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
