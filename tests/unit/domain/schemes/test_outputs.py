from decimal import Decimal

import pytest

from schemes.domain.schemes.observations import ObservationType
from schemes.domain.schemes.outputs import OutputMeasure, OutputType, OutputTypeMeasure, SchemeOutput, SchemeOutputs


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
                OutputType.NEW_SHARED_USE_WALKING_AND_CYCLING_FACILITIES,
                OutputMeasure.MILES,
                OutputTypeMeasure.NEW_SHARED_USE_WALKING_AND_CYCLING_FACILITIES_MILES,
            ),
            (
                OutputType.NEW_SHARED_USE_WALKING_WHEELING_AND_CYCLING_FACILITIES,
                OutputMeasure.MILES,
                OutputTypeMeasure.NEW_SHARED_USE_WALKING_WHEELING_AND_CYCLING_FACILITIES_MILES,
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


class TestSchemeOutput:
    def test_create(self) -> None:
        output = SchemeOutput(
            type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
            value=Decimal(10),
            observation_type=ObservationType.ACTUAL,
        )

        assert (
            output.type_measure == OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES
            and output.value == Decimal(10)
            and output.observation_type == ObservationType.ACTUAL
        )


class TestSchemeOutputs:
    def test_create(self) -> None:
        outputs = SchemeOutputs()

        assert outputs.outputs == []

    def test_get_outputs_is_copy(self) -> None:
        outputs = SchemeOutputs()
        outputs.update_output(
            SchemeOutput(
                type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
                value=Decimal(10),
                observation_type=ObservationType.ACTUAL,
            )
        )

        outputs.outputs.clear()

        assert outputs.outputs

    def test_update_output(self) -> None:
        outputs = SchemeOutputs()
        output = SchemeOutput(
            type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
            value=Decimal(10),
            observation_type=ObservationType.ACTUAL,
        )

        outputs.update_output(output)

        assert outputs.outputs == [output]

    def test_update_outputs(self) -> None:
        outputs = SchemeOutputs()
        output1 = SchemeOutput(
            type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
            value=Decimal(10),
            observation_type=ObservationType.ACTUAL,
        )
        output2 = SchemeOutput(
            type_measure=OutputTypeMeasure.RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY_NUMBER_OF_PARKING_SPACES,
            value=Decimal(20),
            observation_type=ObservationType.ACTUAL,
        )

        outputs.update_outputs(output1, output2)

        assert outputs.outputs == [output1, output2]
