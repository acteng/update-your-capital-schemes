from decimal import Decimal

import pytest

from schemes.domain.schemes.observations import ObservationType
from schemes.domain.schemes.outputs import OutputMeasure, OutputType, OutputTypeMeasure
from schemes.infrastructure.api.observation_types import ObservationTypeModel
from schemes.infrastructure.api.schemes.outputs import CapitalSchemeOutputModel, OutputMeasureModel, OutputTypeModel


class TestOutputTypeModel:
    @pytest.mark.parametrize(
        "type_model, expected_type",
        [
            (OutputTypeModel.NEW_SEGREGATED_CYCLING_FACILITY, OutputType.NEW_SEGREGATED_CYCLING_FACILITY),
            (
                OutputTypeModel.NEW_TEMPORARY_SEGREGATED_CYCLING_FACILITY,
                OutputType.NEW_TEMPORARY_SEGREGATED_CYCLING_FACILITY,
            ),
            (OutputTypeModel.NEW_JUNCTION_TREATMENT, OutputType.NEW_JUNCTION_TREATMENT),
            (OutputTypeModel.NEW_PERMANENT_FOOTWAY, OutputType.NEW_PERMANENT_FOOTWAY),
            (OutputTypeModel.NEW_TEMPORARY_FOOTWAY, OutputType.NEW_TEMPORARY_FOOTWAY),
            (
                OutputTypeModel.NEW_SHARED_USE_WALKING_AND_CYCLING_FACILITIES,
                OutputType.NEW_SHARED_USE_WALKING_AND_CYCLING_FACILITIES,
            ),
            (
                OutputTypeModel.NEW_SHARED_USE_WALKING_WHEELING_AND_CYCLING_FACILITIES,
                OutputType.NEW_SHARED_USE_WALKING_WHEELING_AND_CYCLING_FACILITIES,
            ),
            (OutputTypeModel.IMPROVEMENTS_TO_EXISTING_ROUTE, OutputType.IMPROVEMENTS_TO_EXISTING_ROUTE),
            (OutputTypeModel.AREA_WIDE_TRAFFIC_MANAGEMENT, OutputType.AREA_WIDE_TRAFFIC_MANAGEMENT),
            (OutputTypeModel.BUS_PRIORITY_MEASURES, OutputType.BUS_PRIORITY_MEASURES),
            (OutputTypeModel.SECURE_CYCLE_PARKING, OutputType.SECURE_CYCLE_PARKING),
            (OutputTypeModel.NEW_ROAD_CROSSINGS, OutputType.NEW_ROAD_CROSSINGS),
            (
                OutputTypeModel.RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY,
                OutputType.RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY,
            ),
            (OutputTypeModel.SCHOOL_STREETS, OutputType.SCHOOL_STREETS),
            (OutputTypeModel.UPGRADES_TO_EXISTING_FACILITIES, OutputType.UPGRADES_TO_EXISTING_FACILITIES),
            (OutputTypeModel.E_SCOOTER_TRIALS, OutputType.E_SCOOTER_TRIALS),
            (OutputTypeModel.PARK_AND_CYCLE_STRIDE_FACILITIES, OutputType.PARK_AND_CYCLE_STRIDE_FACILITIES),
            (OutputTypeModel.TRAFFIC_CALMING, OutputType.TRAFFIC_CALMING),
            (OutputTypeModel.WIDENING_EXISTING_FOOTWAY, OutputType.WIDENING_EXISTING_FOOTWAY),
            (OutputTypeModel.OTHER_INTERVENTIONS, OutputType.OTHER_INTERVENTIONS),
        ],
    )
    def test_to_domain(self, type_model: OutputTypeModel, expected_type: OutputType) -> None:
        assert type_model.to_domain() == expected_type


class TestOutputMeasureModel:
    @pytest.mark.parametrize(
        "measure_model, expected_measure",
        [
            (OutputMeasureModel.MILES, OutputMeasure.MILES),
            (OutputMeasureModel.NUMBER_OF_JUNCTIONS, OutputMeasure.NUMBER_OF_JUNCTIONS),
            (OutputMeasureModel.SIZE_OF_AREA, OutputMeasure.SIZE_OF_AREA),
            (OutputMeasureModel.NUMBER_OF_PARKING_SPACES, OutputMeasure.NUMBER_OF_PARKING_SPACES),
            (OutputMeasureModel.NUMBER_OF_CROSSINGS, OutputMeasure.NUMBER_OF_CROSSINGS),
            (OutputMeasureModel.NUMBER_OF_SCHOOL_STREETS, OutputMeasure.NUMBER_OF_SCHOOL_STREETS),
            (OutputMeasureModel.NUMBER_OF_TRIALS, OutputMeasure.NUMBER_OF_TRIALS),
            (OutputMeasureModel.NUMBER_OF_BUS_GATES, OutputMeasure.NUMBER_OF_BUS_GATES),
            (OutputMeasureModel.NUMBER_OF_UPGRADES, OutputMeasure.NUMBER_OF_UPGRADES),
            (OutputMeasureModel.NUMBER_OF_CHILDREN_AFFECTED, OutputMeasure.NUMBER_OF_CHILDREN_AFFECTED),
            (OutputMeasureModel.NUMBER_OF_MEASURES_PLANNED, OutputMeasure.NUMBER_OF_MEASURES_PLANNED),
        ],
    )
    def test_to_domain(self, measure_model: OutputMeasureModel, expected_measure: OutputMeasure) -> None:
        assert measure_model.to_domain() == expected_measure


class TestCapitalSchemeOutputModel:
    def test_to_domain(self) -> None:
        output_model = CapitalSchemeOutputModel(
            type=OutputTypeModel.WIDENING_EXISTING_FOOTWAY,
            measure=OutputMeasureModel.MILES,
            observation_type=ObservationTypeModel.ACTUAL,
            value=Decimal(1.5),
        )

        output_revision = output_model.to_domain()

        assert (
            output_revision.type_measure == OutputTypeMeasure.WIDENING_EXISTING_FOOTWAY_MILES
            and output_revision.observation_type == ObservationType.ACTUAL
            and output_revision.value == Decimal(1.5)
        )
