from schemes.dicts import inverse_dict
from schemes.domain.schemes.outputs import OutputTypeMeasure


class OutputTypeMeasureMapper:
    _IDS = {
        OutputTypeMeasure.WIDENING_EXISTING_FOOTWAY_MILES: 1,
        OutputTypeMeasure.RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY_MILES: 2,
        OutputTypeMeasure.BUS_PRIORITY_MEASURES_MILES: 3,
        OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES: 4,
        OutputTypeMeasure.NEW_SHARED_USE_FACILITIES_WHEELING_MILES: 5,
        OutputTypeMeasure.NEW_SHARED_USE_FACILITIES_MILES: 6,
        OutputTypeMeasure.NEW_TEMPORARY_FOOTWAY_MILES: 7,
        OutputTypeMeasure.NEW_PERMANENT_FOOTWAY_MILES: 8,
        OutputTypeMeasure.NEW_TEMPORARY_SEGREGATED_CYCLING_FACILITY_MILES: 9,
        OutputTypeMeasure.NEW_SEGREGATED_CYCLING_FACILITY_MILES: 10,
        OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_NUMBER_OF_JUNCTIONS: 11,
        OutputTypeMeasure.NEW_PERMANENT_FOOTWAY_NUMBER_OF_JUNCTIONS: 12,
        OutputTypeMeasure.NEW_JUNCTION_TREATMENT_NUMBER_OF_JUNCTIONS: 13,
        OutputTypeMeasure.NEW_TEMPORARY_SEGREGATED_CYCLING_FACILITY_NUMBER_OF_JUNCTIONS: 14,
        OutputTypeMeasure.NEW_SEGREGATED_CYCLING_FACILITY_NUMBER_OF_JUNCTIONS: 15,
        OutputTypeMeasure.AREA_WIDE_TRAFFIC_MANAGEMENT_SIZE_OF_AREA: 16,
        OutputTypeMeasure.PARK_AND_CYCLE_STRIDE_FACILITIES_NUMBER_OF_PARKING_SPACES: 17,
        OutputTypeMeasure.RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY_NUMBER_OF_PARKING_SPACES: 18,
        OutputTypeMeasure.SECURE_CYCLE_PARKING_NUMBER_OF_PARKING_SPACES: 19,
        OutputTypeMeasure.NEW_ROAD_CROSSINGS_NUMBER_OF_CROSSINGS: 20,
        OutputTypeMeasure.SCHOOL_STREETS_NUMBER_OF_SCHOOL_STREETS: 21,
        OutputTypeMeasure.E_SCOOTER_TRIALS_NUMBER_OF_TRIALS: 22,
        OutputTypeMeasure.BUS_PRIORITY_MEASURES_NUMBER_OF_BUS_GATES: 23,
        OutputTypeMeasure.UPGRADES_TO_EXISTING_FACILITIES_NUMBER_OF_UPGRADES: 24,
        OutputTypeMeasure.SCHOOL_STREETS_NUMBER_OF_CHILDREN_AFFECTED: 25,
        OutputTypeMeasure.OTHER_INTERVENTIONS_NUMBER_OF_MEASURES_PLANNED: 26,
        OutputTypeMeasure.TRAFFIC_CALMING_NUMBER_OF_MEASURES_PLANNED: 27,
    }

    def to_id(self, output_type_measure: OutputTypeMeasure) -> int:
        return self._IDS[output_type_measure]

    def to_domain(self, id_: int) -> OutputTypeMeasure:
        return inverse_dict(self._IDS)[id_]
