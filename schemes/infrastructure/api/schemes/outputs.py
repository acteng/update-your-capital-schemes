from datetime import datetime
from decimal import Decimal
from enum import Enum

from schemes.domain.dates import DateRange
from schemes.domain.schemes.outputs import OutputMeasure, OutputRevision, OutputType, OutputTypeMeasure
from schemes.infrastructure.api.base import BaseModel
from schemes.infrastructure.api.observation_types import ObservationTypeModel


class OutputTypeModel(str, Enum):
    NEW_SEGREGATED_CYCLING_FACILITY = "new segregated cycling facility"
    NEW_TEMPORARY_SEGREGATED_CYCLING_FACILITY = "new temporary segregated cycling facility"
    NEW_JUNCTION_TREATMENT = "new junction treatment"
    NEW_PERMANENT_FOOTWAY = "new permanent footway"
    NEW_TEMPORARY_FOOTWAY = "new temporary footway"
    NEW_SHARED_USE_WALKING_AND_CYCLING_FACILITIES = "new shared use (walking and cycling) facilities"
    NEW_SHARED_USE_WALKING_WHEELING_AND_CYCLING_FACILITIES = "new shared use (walking, wheeling & cycling) facilities"
    IMPROVEMENTS_TO_EXISTING_ROUTE = "improvements to make an existing walking/cycle route safer"
    AREA_WIDE_TRAFFIC_MANAGEMENT = "area-wide traffic management (including by TROs (both permanent and experimental))"
    BUS_PRIORITY_MEASURES = "bus priority measures that also enable active travel (for example, bus gates)"
    SECURE_CYCLE_PARKING = "provision of secure cycle parking facilities"
    NEW_ROAD_CROSSINGS = "new road crossings"
    RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY = "restriction or reduction of car parking availability"
    SCHOOL_STREETS = "school streets"
    UPGRADES_TO_EXISTING_FACILITIES = "upgrades to existing facilities (e.g. surfacing, signage, signals)"
    E_SCOOTER_TRIALS = "e-scooter trials"
    PARK_AND_CYCLE_STRIDE_FACILITIES = "park and cycle/stride facilities"
    TRAFFIC_CALMING = "traffic calming (e.g. lane closures, reducing speed limits)"
    WIDENING_EXISTING_FOOTWAY = "widening existing footway"
    OTHER_INTERVENTIONS = "other interventions"

    def to_domain(self) -> OutputType:
        return OutputType[self.name]


class OutputMeasureModel(str, Enum):
    MILES = "miles"
    NUMBER_OF_JUNCTIONS = "number of junctions"
    SIZE_OF_AREA = "size of area"
    NUMBER_OF_PARKING_SPACES = "number of parking spaces"
    NUMBER_OF_CROSSINGS = "number of crossings"
    NUMBER_OF_SCHOOL_STREETS = "number of school streets"
    NUMBER_OF_TRIALS = "number of trials"
    NUMBER_OF_BUS_GATES = "number of bus gates"
    NUMBER_OF_UPGRADES = "number of upgrades"
    NUMBER_OF_CHILDREN_AFFECTED = "number of children affected"
    NUMBER_OF_MEASURES_PLANNED = "number of measures planned"

    def to_domain(self) -> OutputMeasure:
        return OutputMeasure[self.name]


class CapitalSchemeOutputModel(BaseModel):
    type: OutputTypeModel
    measure: OutputMeasureModel
    observation_type: ObservationTypeModel
    value: Decimal

    def to_domain(self) -> OutputRevision:
        # TODO: id, effective
        return OutputRevision(
            id_=0,
            effective=DateRange(date_from=datetime.min, date_to=None),
            type_measure=OutputTypeMeasure.from_type_and_measure(self.type.to_domain(), self.measure.to_domain()),
            value=self.value,
            observation_type=self.observation_type.to_domain(),
        )
