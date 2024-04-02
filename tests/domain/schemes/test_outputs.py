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
    SchemeOutputs,
)


class TestSchemeOutputs:
    def test_create(self) -> None:
        outputs = SchemeOutputs()

        assert outputs.output_revisions == []

    def test_get_output_revisions_is_copy(self) -> None:
        outputs = SchemeOutputs()
        outputs.update_output(
            OutputRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
                value=Decimal(10),
                observation_type=ObservationType.ACTUAL,
            )
        )

        outputs.output_revisions.clear()

        assert outputs.output_revisions

    def test_get_current_output_revisions(self) -> None:
        outputs = SchemeOutputs()
        output_revision1 = OutputRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1), datetime(2020, 2, 1)),
            type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
            value=Decimal(10),
            observation_type=ObservationType.PLANNED,
        )
        output_revision2 = OutputRevision(
            id_=2,
            effective=DateRange(datetime(2020, 1, 1), None),
            type_measure=OutputTypeMeasure.RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY_NUMBER_OF_PARKING_SPACES,
            value=Decimal(20),
            observation_type=ObservationType.PLANNED,
        )
        outputs.update_outputs(output_revision1, output_revision2)

        assert outputs.current_output_revisions == [output_revision2]

    def test_update_output(self) -> None:
        outputs = SchemeOutputs()
        output_revision = OutputRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1), None),
            type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
            value=Decimal(10),
            observation_type=ObservationType.ACTUAL,
        )

        outputs.update_output(output_revision)

        assert outputs.output_revisions == [output_revision]

    def test_update_outputs(self) -> None:
        outputs = SchemeOutputs()
        output_revision1 = OutputRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1), None),
            type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
            value=Decimal(10),
            observation_type=ObservationType.ACTUAL,
        )
        output_revision2 = OutputRevision(
            id_=2,
            effective=DateRange(datetime(2020, 1, 1), None),
            type_measure=OutputTypeMeasure.RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY_NUMBER_OF_PARKING_SPACES,
            value=Decimal(20),
            observation_type=ObservationType.ACTUAL,
        )

        outputs.update_outputs(output_revision1, output_revision2)

        assert outputs.output_revisions == [output_revision1, output_revision2]


class TestOutputRevision:
    def test_create(self) -> None:
        output_revision = OutputRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1), None),
            type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
            value=Decimal(10),
            observation_type=ObservationType.ACTUAL,
        )

        assert (
            output_revision.id == 1
            and output_revision.effective == DateRange(datetime(2020, 1, 1), None)
            and output_revision.type_measure == OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES
            and output_revision.value == Decimal(10)
            and output_revision.observation_type == ObservationType.ACTUAL
        )


class TestOutputTypeMeasure:
    @pytest.mark.parametrize(
        "type_, measure, expected_type_measure",
        [
            (
                OutputType.NEW_SEGREGATED_CYCLING_FACILITY,
                OutputMeasure.MILES,
                OutputTypeMeasure.NEW_SEGREGATED_CYCLING_FACILITY_MILES,
            ),
            (
                OutputType.NEW_SEGREGATED_CYCLING_FACILITY,
                OutputMeasure.NUMBER_OF_JUNCTIONS,
                OutputTypeMeasure.NEW_SEGREGATED_CYCLING_FACILITY_NUMBER_OF_JUNCTIONS,
            ),
            (
                OutputType.NEW_TEMPORARY_SEGREGATED_CYCLING_FACILITY,
                OutputMeasure.MILES,
                OutputTypeMeasure.NEW_TEMPORARY_SEGREGATED_CYCLING_FACILITY_MILES,
            ),
            (
                OutputType.NEW_TEMPORARY_SEGREGATED_CYCLING_FACILITY,
                OutputMeasure.NUMBER_OF_JUNCTIONS,
                OutputTypeMeasure.NEW_TEMPORARY_SEGREGATED_CYCLING_FACILITY_NUMBER_OF_JUNCTIONS,
            ),
            (
                OutputType.NEW_JUNCTION_TREATMENT,
                OutputMeasure.NUMBER_OF_JUNCTIONS,
                OutputTypeMeasure.NEW_JUNCTION_TREATMENT_NUMBER_OF_JUNCTIONS,
            ),
            (OutputType.NEW_PERMANENT_FOOTWAY, OutputMeasure.MILES, OutputTypeMeasure.NEW_PERMANENT_FOOTWAY_MILES),
            (
                OutputType.NEW_PERMANENT_FOOTWAY,
                OutputMeasure.NUMBER_OF_JUNCTIONS,
                OutputTypeMeasure.NEW_PERMANENT_FOOTWAY_NUMBER_OF_JUNCTIONS,
            ),
            (OutputType.NEW_TEMPORARY_FOOTWAY, OutputMeasure.MILES, OutputTypeMeasure.NEW_TEMPORARY_FOOTWAY_MILES),
            (
                OutputType.NEW_SHARED_USE_FACILITIES,
                OutputMeasure.MILES,
                OutputTypeMeasure.NEW_SHARED_USE_FACILITIES_MILES,
            ),
            (
                OutputType.NEW_SHARED_USE_FACILITIES_WHEELING,
                OutputMeasure.MILES,
                OutputTypeMeasure.NEW_SHARED_USE_FACILITIES_WHEELING_MILES,
            ),
            (
                OutputType.IMPROVEMENTS_TO_EXISTING_ROUTE,
                OutputMeasure.MILES,
                OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
            ),
            (
                OutputType.IMPROVEMENTS_TO_EXISTING_ROUTE,
                OutputMeasure.NUMBER_OF_JUNCTIONS,
                OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_NUMBER_OF_JUNCTIONS,
            ),
            (
                OutputType.AREA_WIDE_TRAFFIC_MANAGEMENT,
                OutputMeasure.SIZE_OF_AREA,
                OutputTypeMeasure.AREA_WIDE_TRAFFIC_MANAGEMENT_SIZE_OF_AREA,
            ),
            (OutputType.BUS_PRIORITY_MEASURES, OutputMeasure.MILES, OutputTypeMeasure.BUS_PRIORITY_MEASURES_MILES),
            (
                OutputType.BUS_PRIORITY_MEASURES,
                OutputMeasure.NUMBER_OF_BUS_GATES,
                OutputTypeMeasure.BUS_PRIORITY_MEASURES_NUMBER_OF_BUS_GATES,
            ),
            (
                OutputType.SECURE_CYCLE_PARKING,
                OutputMeasure.NUMBER_OF_PARKING_SPACES,
                OutputTypeMeasure.SECURE_CYCLE_PARKING_NUMBER_OF_PARKING_SPACES,
            ),
            (
                OutputType.NEW_ROAD_CROSSINGS,
                OutputMeasure.NUMBER_OF_CROSSINGS,
                OutputTypeMeasure.NEW_ROAD_CROSSINGS_NUMBER_OF_CROSSINGS,
            ),
            (
                OutputType.RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY,
                OutputMeasure.MILES,
                OutputTypeMeasure.RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY_MILES,
            ),
            (
                OutputType.RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY,
                OutputMeasure.NUMBER_OF_PARKING_SPACES,
                OutputTypeMeasure.RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY_NUMBER_OF_PARKING_SPACES,
            ),
            (
                OutputType.SCHOOL_STREETS,
                OutputMeasure.NUMBER_OF_SCHOOL_STREETS,
                OutputTypeMeasure.SCHOOL_STREETS_NUMBER_OF_SCHOOL_STREETS,
            ),
            (
                OutputType.SCHOOL_STREETS,
                OutputMeasure.NUMBER_OF_CHILDREN_AFFECTED,
                OutputTypeMeasure.SCHOOL_STREETS_NUMBER_OF_CHILDREN_AFFECTED,
            ),
            (
                OutputType.UPGRADES_TO_EXISTING_FACILITIES,
                OutputMeasure.NUMBER_OF_UPGRADES,
                OutputTypeMeasure.UPGRADES_TO_EXISTING_FACILITIES_NUMBER_OF_UPGRADES,
            ),
            (
                OutputType.E_SCOOTER_TRIALS,
                OutputMeasure.NUMBER_OF_TRIALS,
                OutputTypeMeasure.E_SCOOTER_TRIALS_NUMBER_OF_TRIALS,
            ),
            (
                OutputType.PARK_AND_CYCLE_STRIDE_FACILITIES,
                OutputMeasure.NUMBER_OF_PARKING_SPACES,
                OutputTypeMeasure.PARK_AND_CYCLE_STRIDE_FACILITIES_NUMBER_OF_PARKING_SPACES,
            ),
            (
                OutputType.TRAFFIC_CALMING,
                OutputMeasure.NUMBER_OF_MEASURES_PLANNED,
                OutputTypeMeasure.TRAFFIC_CALMING_NUMBER_OF_MEASURES_PLANNED,
            ),
            (
                OutputType.WIDENING_EXISTING_FOOTWAY,
                OutputMeasure.MILES,
                OutputTypeMeasure.WIDENING_EXISTING_FOOTWAY_MILES,
            ),
            (
                OutputType.OTHER_INTERVENTIONS,
                OutputMeasure.NUMBER_OF_MEASURES_PLANNED,
                OutputTypeMeasure.OTHER_INTERVENTIONS_NUMBER_OF_MEASURES_PLANNED,
            ),
        ],
    )
    def test_get_from_type_and_measure(
        self, type_: OutputType, measure: OutputMeasure, expected_type_measure: OutputTypeMeasure
    ) -> None:
        assert OutputTypeMeasure.from_type_and_measure(type_, measure) == expected_type_measure

    def test_cannot_get_from_type_and_measure_when_unknown(self) -> None:
        with pytest.raises(
            ValueError,
            match="No such output type measure for type IMPROVEMENTS_TO_EXISTING_ROUTE and measure NUMBER_OF_PARKING_SPACES",
        ):
            OutputTypeMeasure.from_type_and_measure(
                OutputType.IMPROVEMENTS_TO_EXISTING_ROUTE, OutputMeasure.NUMBER_OF_PARKING_SPACES
            )
