from __future__ import annotations

from decimal import Decimal
from enum import Enum, IntEnum, auto, unique

from schemes.domain.schemes.dates import DateRange
from schemes.domain.schemes.observations import ObservationType


class SchemeOutputs:
    def __init__(self) -> None:
        self._output_revisions: list[OutputRevision] = []

    @property
    def output_revisions(self) -> list[OutputRevision]:
        return list(self._output_revisions)

    @property
    def current_output_revisions(self) -> list[OutputRevision]:
        return [revision for revision in self._output_revisions if revision.effective.date_to is None]

    def update_output(self, output_revision: OutputRevision) -> None:
        self._output_revisions.append(output_revision)

    def update_outputs(self, *output_revisions: OutputRevision) -> None:
        for output_revision in output_revisions:
            self.update_output(output_revision)


class OutputRevision:
    def __init__(
        self, effective: DateRange, type_measure: OutputTypeMeasure, value: Decimal, observation_type: ObservationType
    ):
        self.effective = effective
        self.type_measure = type_measure
        self.value = value
        self.observation_type = observation_type


class OutputType(IntEnum):
    NEW_SEGREGATED_CYCLING_FACILITY = auto()
    NEW_TEMPORARY_SEGREGATED_CYCLING_FACILITY = auto()
    NEW_JUNCTION_TREATMENT = auto()
    NEW_PERMANENT_FOOTWAY = auto()
    NEW_TEMPORARY_FOOTWAY = auto()
    NEW_SHARED_USE_FACILITIES = auto()
    NEW_SHARED_USE_FACILITIES_WHEELING = auto()
    IMPROVEMENTS_TO_EXISTING_ROUTE = auto()
    AREA_WIDE_TRAFFIC_MANAGEMENT = auto()
    BUS_PRIORITY_MEASURES = auto()
    SECURE_CYCLE_PARKING = auto()
    NEW_ROAD_CROSSINGS = auto()
    RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY = auto()
    SCHOOL_STREETS = auto()
    UPGRADES_TO_EXISTING_FACILITIES = auto()
    E_SCOOTER_TRIALS = auto()
    PARK_AND_CYCLE_STRIDE_FACILITIES = auto()
    TRAFFIC_CALMING = auto()
    WIDENING_EXISTING_FOOTWAY = auto()
    OTHER_INTERVENTIONS = auto()


class OutputMeasure(IntEnum):
    MILES = auto()
    NUMBER_OF_JUNCTIONS = auto()
    SIZE_OF_AREA = auto()
    NUMBER_OF_PARKING_SPACES = auto()
    NUMBER_OF_CROSSINGS = auto()
    NUMBER_OF_SCHOOL_STREETS = auto()
    NUMBER_OF_TRIALS = auto()
    NUMBER_OF_BUS_GATES = auto()
    NUMBER_OF_UPGRADES = auto()
    NUMBER_OF_CHILDREN_AFFECTED = auto()
    NUMBER_OF_MEASURES_PLANNED = auto()


@unique
class OutputTypeMeasure(Enum):
    NEW_SEGREGATED_CYCLING_FACILITY_MILES = (OutputType.NEW_SEGREGATED_CYCLING_FACILITY, OutputMeasure.MILES)
    NEW_SEGREGATED_CYCLING_FACILITY_NUMBER_OF_JUNCTIONS = (
        OutputType.NEW_SEGREGATED_CYCLING_FACILITY,
        OutputMeasure.NUMBER_OF_JUNCTIONS,
    )
    NEW_TEMPORARY_SEGREGATED_CYCLING_FACILITY_MILES = (
        OutputType.NEW_TEMPORARY_SEGREGATED_CYCLING_FACILITY,
        OutputMeasure.MILES,
    )
    NEW_TEMPORARY_SEGREGATED_CYCLING_FACILITY_NUMBER_OF_JUNCTIONS = (
        OutputType.NEW_TEMPORARY_SEGREGATED_CYCLING_FACILITY,
        OutputMeasure.NUMBER_OF_JUNCTIONS,
    )
    NEW_JUNCTION_TREATMENT_NUMBER_OF_JUNCTIONS = (OutputType.NEW_JUNCTION_TREATMENT, OutputMeasure.NUMBER_OF_JUNCTIONS)
    NEW_PERMANENT_FOOTWAY_MILES = (OutputType.NEW_PERMANENT_FOOTWAY, OutputMeasure.MILES)
    NEW_PERMANENT_FOOTWAY_NUMBER_OF_JUNCTIONS = (OutputType.NEW_PERMANENT_FOOTWAY, OutputMeasure.NUMBER_OF_JUNCTIONS)
    NEW_TEMPORARY_FOOTWAY_MILES = (OutputType.NEW_TEMPORARY_FOOTWAY, OutputMeasure.MILES)
    NEW_SHARED_USE_FACILITIES_MILES = (OutputType.NEW_SHARED_USE_FACILITIES, OutputMeasure.MILES)
    NEW_SHARED_USE_FACILITIES_WHEELING_MILES = (OutputType.NEW_SHARED_USE_FACILITIES_WHEELING, OutputMeasure.MILES)
    IMPROVEMENTS_TO_EXISTING_ROUTE_MILES = (OutputType.IMPROVEMENTS_TO_EXISTING_ROUTE, OutputMeasure.MILES)
    IMPROVEMENTS_TO_EXISTING_ROUTE_NUMBER_OF_JUNCTIONS = (
        OutputType.IMPROVEMENTS_TO_EXISTING_ROUTE,
        OutputMeasure.NUMBER_OF_JUNCTIONS,
    )
    AREA_WIDE_TRAFFIC_MANAGEMENT_SIZE_OF_AREA = (OutputType.AREA_WIDE_TRAFFIC_MANAGEMENT, OutputMeasure.SIZE_OF_AREA)
    BUS_PRIORITY_MEASURES_MILES = (OutputType.BUS_PRIORITY_MEASURES, OutputMeasure.MILES)
    BUS_PRIORITY_MEASURES_NUMBER_OF_BUS_GATES = (OutputType.BUS_PRIORITY_MEASURES, OutputMeasure.NUMBER_OF_BUS_GATES)
    SECURE_CYCLE_PARKING_NUMBER_OF_PARKING_SPACES = (
        OutputType.SECURE_CYCLE_PARKING,
        OutputMeasure.NUMBER_OF_PARKING_SPACES,
    )
    NEW_ROAD_CROSSINGS_NUMBER_OF_CROSSINGS = (OutputType.NEW_ROAD_CROSSINGS, OutputMeasure.NUMBER_OF_CROSSINGS)
    RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY_MILES = (
        OutputType.RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY,
        OutputMeasure.MILES,
    )
    RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY_NUMBER_OF_PARKING_SPACES = (
        OutputType.RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY,
        OutputMeasure.NUMBER_OF_PARKING_SPACES,
    )
    SCHOOL_STREETS_NUMBER_OF_SCHOOL_STREETS = (OutputType.SCHOOL_STREETS, OutputMeasure.NUMBER_OF_SCHOOL_STREETS)
    SCHOOL_STREETS_NUMBER_OF_CHILDREN_AFFECTED = (OutputType.SCHOOL_STREETS, OutputMeasure.NUMBER_OF_CHILDREN_AFFECTED)
    UPGRADES_TO_EXISTING_FACILITIES_NUMBER_OF_UPGRADES = (
        OutputType.UPGRADES_TO_EXISTING_FACILITIES,
        OutputMeasure.NUMBER_OF_UPGRADES,
    )
    E_SCOOTER_TRIALS_NUMBER_OF_TRIALS = (OutputType.E_SCOOTER_TRIALS, OutputMeasure.NUMBER_OF_TRIALS)
    PARK_AND_CYCLE_STRIDE_FACILITIES_NUMBER_OF_PARKING_SPACES = (
        OutputType.PARK_AND_CYCLE_STRIDE_FACILITIES,
        OutputMeasure.NUMBER_OF_PARKING_SPACES,
    )
    TRAFFIC_CALMING_NUMBER_OF_MEASURES_PLANNED = (OutputType.TRAFFIC_CALMING, OutputMeasure.NUMBER_OF_MEASURES_PLANNED)
    WIDENING_EXISTING_FOOTWAY_MILES = (OutputType.WIDENING_EXISTING_FOOTWAY, OutputMeasure.MILES)
    OTHER_INTERVENTIONS_NUMBER_OF_MEASURES_PLANNED = (
        OutputType.OTHER_INTERVENTIONS,
        OutputMeasure.NUMBER_OF_MEASURES_PLANNED,
    )

    def __init__(self, type_: OutputType, measure: OutputMeasure):
        self.type = type_
        self.measure = measure

    @classmethod
    def from_type_and_measure(cls, type_: OutputType, measure: OutputMeasure) -> OutputTypeMeasure:
        member = next((member for member in cls if member.type == type_ and member.measure == measure), None)

        if not member:
            raise ValueError(f"No such output type measure for type {type_.name} and measure {measure.name}")

        return member
