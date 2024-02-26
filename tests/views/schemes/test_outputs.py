from datetime import datetime
from decimal import Decimal

import pytest

from schemes.domain.dates import DateRange
from schemes.domain.schemes import (
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
    def test_from_domain(self) -> None:
        output_revision = OutputRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1, 12), datetime(2020, 1, 31, 13)),
            type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
            value=Decimal(10),
            observation_type=ObservationType.ACTUAL,
        )

        output_revision_repr = OutputRevisionRepr.from_domain(output_revision)

        assert output_revision_repr == OutputRevisionRepr(
            id=1,
            effective_date_from="2020-01-01T12:00:00",
            effective_date_to="2020-01-31T13:00:00",
            type=OutputTypeRepr.IMPROVEMENTS_TO_EXISTING_ROUTE,
            measure=OutputMeasureRepr.MILES,
            value="10",
            observation_type=ObservationTypeRepr.ACTUAL,
        )

    def test_from_domain_when_no_effective_date_to(self) -> None:
        output_revision = OutputRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1), None),
            type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
            value=Decimal(10),
            observation_type=ObservationType.ACTUAL,
        )

        output_revision_repr = OutputRevisionRepr.from_domain(output_revision)

        assert output_revision_repr.effective_date_to is None

    def test_to_domain(self) -> None:
        output_revision_repr = OutputRevisionRepr(
            id=1,
            effective_date_from="2020-01-01T12:00:00",
            effective_date_to="2020-01-31T13:00:00",
            type=OutputTypeRepr.IMPROVEMENTS_TO_EXISTING_ROUTE,
            measure=OutputMeasureRepr.MILES,
            value="10",
            observation_type=ObservationTypeRepr.ACTUAL,
        )

        output_revision = output_revision_repr.to_domain()

        assert (
            output_revision.id == 1
            and output_revision.effective == DateRange(datetime(2020, 1, 1, 12), datetime(2020, 1, 31, 13))
            and output_revision.type_measure == OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES
            and output_revision.value == Decimal(10)
            and output_revision.observation_type == ObservationType.ACTUAL
        )

    def test_to_domain_when_no_effective_date_to(self) -> None:
        output_revision_repr = OutputRevisionRepr(
            id=1,
            effective_date_from="2020-01-01",
            effective_date_to=None,
            type=OutputTypeRepr.IMPROVEMENTS_TO_EXISTING_ROUTE,
            measure=OutputMeasureRepr.MILES,
            value="10",
            observation_type=ObservationTypeRepr.ACTUAL,
        )

        output_revision = output_revision_repr.to_domain()

        assert output_revision.effective.date_to is None


@pytest.mark.parametrize(
    "type_, type_repr",
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
class TestOutputTypeRepr:
    def test_from_domain(self, type_: OutputType, type_repr: str) -> None:
        assert OutputTypeRepr.from_domain(type_).value == type_repr

    def test_to_domain(self, type_: OutputType, type_repr: str) -> None:
        assert OutputTypeRepr(type_repr).to_domain() == type_


@pytest.mark.parametrize(
    "measure, measure_repr",
    [
        (OutputMeasure.MILES, "miles"),
        (OutputMeasure.NUMBER_OF_JUNCTIONS, "number of junctions"),
        (OutputMeasure.SIZE_OF_AREA, "size of area"),
        (OutputMeasure.NUMBER_OF_PARKING_SPACES, "number of parking spaces"),
        (OutputMeasure.NUMBER_OF_CROSSINGS, "number of crossings"),
        (OutputMeasure.NUMBER_OF_SCHOOL_STREETS, "number of school streets"),
        (OutputMeasure.NUMBER_OF_TRIALS, "number of trials"),
        (OutputMeasure.NUMBER_OF_BUS_GATES, "number of bus gates"),
        (OutputMeasure.NUMBER_OF_UPGRADES, "number of upgrades"),
        (OutputMeasure.NUMBER_OF_CHILDREN_AFFECTED, "number of children affected"),
        (OutputMeasure.NUMBER_OF_MEASURES_PLANNED, "number of measures planned"),
    ],
)
class TestOutputMeasureRepr:
    def test_from_domain(self, measure: OutputMeasure, measure_repr: str) -> None:
        assert OutputMeasureRepr.from_domain(measure).value == measure_repr

    def test_to_domain(self, measure: OutputMeasure, measure_repr: str) -> None:
        assert OutputMeasureRepr(measure_repr).to_domain() == measure
