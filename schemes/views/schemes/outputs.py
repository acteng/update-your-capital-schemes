from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum, unique
from itertools import groupby
from typing import Iterator

from schemes.domain.schemes import (
    DateRange,
    ObservationType,
    OutputMeasure,
    OutputRevision,
    OutputType,
    OutputTypeMeasure,
)
from schemes.views.schemes.observations import ObservationTypeRepr


@dataclass(frozen=True)
class SchemeOutputsContext:
    outputs: list[SchemeOutputRowContext]

    @classmethod
    def from_domain(cls, output_revisions: list[OutputRevision]) -> SchemeOutputsContext:
        return cls(
            outputs=[
                SchemeOutputRowContext(
                    type=OutputTypeContext.from_domain(type_),
                    measure=OutputMeasureContext.from_domain(measure),
                    planned=cls._get_value(group, ObservationType.PLANNED),
                )
                for (type_, measure), group in groupby(
                    sorted(output_revisions, key=SchemeOutputsContext._by_type_and_measure),
                    cls._by_type_and_measure,
                )
            ]
        )

    @staticmethod
    def _by_type_and_measure(output_revision: OutputRevision) -> tuple[OutputType, OutputMeasure]:
        return output_revision.type_measure.type, output_revision.type_measure.measure

    @staticmethod
    def _get_value(output_revisions: Iterator[OutputRevision], observation_type: ObservationType) -> Decimal | None:
        revisions = (revision.value for revision in output_revisions if revision.observation_type == observation_type)
        return next(revisions, None)


@dataclass(frozen=True)
class SchemeOutputRowContext:
    type: OutputTypeContext
    measure: OutputMeasureContext
    planned: Decimal | None


@dataclass(frozen=True)
class OutputTypeContext:
    name: str
    _NAMES = {
        OutputType.NEW_SEGREGATED_CYCLING_FACILITY: "New segregated cycling facility",
        OutputType.NEW_TEMPORARY_SEGREGATED_CYCLING_FACILITY: "New temporary segregated cycling facility",
        OutputType.NEW_JUNCTION_TREATMENT: "New junction treatment",
        OutputType.NEW_PERMANENT_FOOTWAY: "New permanent footway",
        OutputType.NEW_TEMPORARY_FOOTWAY: "New temporary footway",
        OutputType.NEW_SHARED_USE_FACILITIES: "New shared use (walking and cycling) facilities",
        OutputType.NEW_SHARED_USE_FACILITIES_WHEELING: "New shared use (walking, wheeling & cycling) facilities",
        OutputType.IMPROVEMENTS_TO_EXISTING_ROUTE: "Improvements to make an existing walking/cycle route safer",
        OutputType.AREA_WIDE_TRAFFIC_MANAGEMENT: "Area-wide traffic management (including by TROs (both permanent and experimental))",
        OutputType.BUS_PRIORITY_MEASURES: "Bus priority measures that also enable active travel (for example, bus gates)",
        OutputType.SECURE_CYCLE_PARKING: "Provision of secure cycle parking facilities",
        OutputType.NEW_ROAD_CROSSINGS: "New road crossings",
        OutputType.RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY: "Restriction or reduction of car parking availability",
        OutputType.SCHOOL_STREETS: "School streets",
        OutputType.UPGRADES_TO_EXISTING_FACILITIES: "Upgrades to existing facilities (e.g. surfacing, signage, signals)",
        OutputType.E_SCOOTER_TRIALS: "E-scooter trials",
        OutputType.PARK_AND_CYCLE_STRIDE_FACILITIES: "Park and cycle/stride facilities",
        OutputType.TRAFFIC_CALMING: "Traffic calming (e.g. lane closures, reducing speed limits)",
        OutputType.WIDENING_EXISTING_FOOTWAY: "Widening existing footway",
        OutputType.OTHER_INTERVENTIONS: "Other interventions",
    }

    @classmethod
    def from_domain(cls, type_: OutputType) -> OutputTypeContext:
        return cls(name=cls._NAMES[type_])


@dataclass(frozen=True)
class OutputMeasureContext:
    name: str
    _NAMES = {
        OutputMeasure.MILES: "Miles",
        OutputMeasure.NUMBER_OF_JUNCTIONS: "Number of junctions",
        OutputMeasure.SIZE_OF_AREA: "Size of area",
        OutputMeasure.NUMBER_OF_PARKING_SPACES: "Number of parking spaces",
        OutputMeasure.NUMBER_OF_CROSSINGS: "Number of crossings",
        OutputMeasure.NUMBER_OF_SCHOOL_STREETS: "Number of school streets",
        OutputMeasure.NUMBER_OF_TRIALS: "Number of trials",
        OutputMeasure.NUMBER_OF_BUS_GATES: "Number of bus gates",
        OutputMeasure.NUMBER_OF_UPGRADES: "Number of upgrades",
        OutputMeasure.NUMBER_OF_CHILDREN_AFFECTED: "Number of children affected",
        OutputMeasure.NUMBER_OF_MEASURES_PLANNED: "Number of measures planned",
    }

    @classmethod
    def from_domain(cls, measure: OutputMeasure) -> OutputMeasureContext:
        return cls(name=cls._NAMES[measure])


@dataclass(frozen=True)
class OutputRevisionRepr:
    id: int
    effective_date_from: str
    effective_date_to: str | None
    type: OutputTypeRepr
    measure: OutputMeasureRepr
    value: str
    observation_type: ObservationTypeRepr

    def to_domain(self) -> OutputRevision:
        return OutputRevision(
            id_=self.id,
            effective=DateRange(
                date_from=datetime.fromisoformat(self.effective_date_from),
                date_to=datetime.fromisoformat(self.effective_date_to) if self.effective_date_to else None,
            ),
            type_measure=OutputTypeMeasure.from_type_and_measure(self.type.to_domain(), self.measure.to_domain()),
            value=Decimal(self.value),
            observation_type=self.observation_type.to_domain(),
        )


@unique
class OutputTypeRepr(Enum):
    NEW_SEGREGATED_CYCLING_FACILITY = "New segregated cycling facility"
    NEW_TEMPORARY_SEGREGATED_CYCLING_FACILITY = "New temporary segregated cycling facility"
    NEW_JUNCTION_TREATMENT = "New junction treatment"
    NEW_PERMANENT_FOOTWAY = "New permanent footway"
    NEW_TEMPORARY_FOOTWAY = "New temporary footway"
    NEW_SHARED_USE_FACILITIES = "New shared use (walking and cycling) facilities"
    NEW_SHARED_USE_FACILITIES_WHEELING = "New shared use (walking, wheeling & cycling) facilities"
    IMPROVEMENTS_TO_EXISTING_ROUTE = "Improvements to make an existing walking/cycle route safer"
    AREA_WIDE_TRAFFIC_MANAGEMENT = "Area-wide traffic management (including by TROs (both permanent and experimental))"
    BUS_PRIORITY_MEASURES = "Bus priority measures that also enable active travel (for example, bus gates)"
    SECURE_CYCLE_PARKING = "Provision of secure cycle parking facilities"
    NEW_ROAD_CROSSINGS = "New road crossings"
    RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY = "Restriction or reduction of car parking availability"
    SCHOOL_STREETS = "School streets"
    UPGRADES_TO_EXISTING_FACILITIES = "Upgrades to existing facilities (e.g. surfacing, signage, signals)"
    E_SCOOTER_TRIALS = "E-scooter trials"
    PARK_AND_CYCLE_STRIDE_FACILITIES = "Park and cycle/stride facilities"
    TRAFFIC_CALMING = "Traffic calming (e.g. lane closures, reducing speed limits)"
    WIDENING_EXISTING_FOOTWAY = "Widening existing footway"
    OTHER_INTERVENTIONS = "Other interventions"

    def to_domain(self) -> OutputType:
        members = {
            OutputTypeRepr.NEW_SEGREGATED_CYCLING_FACILITY: OutputType.NEW_SEGREGATED_CYCLING_FACILITY,
            OutputTypeRepr.NEW_TEMPORARY_SEGREGATED_CYCLING_FACILITY: OutputType.NEW_TEMPORARY_SEGREGATED_CYCLING_FACILITY,
            OutputTypeRepr.NEW_JUNCTION_TREATMENT: OutputType.NEW_JUNCTION_TREATMENT,
            OutputTypeRepr.NEW_PERMANENT_FOOTWAY: OutputType.NEW_PERMANENT_FOOTWAY,
            OutputTypeRepr.NEW_TEMPORARY_FOOTWAY: OutputType.NEW_TEMPORARY_FOOTWAY,
            OutputTypeRepr.NEW_SHARED_USE_FACILITIES: OutputType.NEW_SHARED_USE_FACILITIES,
            OutputTypeRepr.NEW_SHARED_USE_FACILITIES_WHEELING: OutputType.NEW_SHARED_USE_FACILITIES_WHEELING,
            OutputTypeRepr.IMPROVEMENTS_TO_EXISTING_ROUTE: OutputType.IMPROVEMENTS_TO_EXISTING_ROUTE,
            OutputTypeRepr.AREA_WIDE_TRAFFIC_MANAGEMENT: OutputType.AREA_WIDE_TRAFFIC_MANAGEMENT,
            OutputTypeRepr.BUS_PRIORITY_MEASURES: OutputType.BUS_PRIORITY_MEASURES,
            OutputTypeRepr.SECURE_CYCLE_PARKING: OutputType.SECURE_CYCLE_PARKING,
            OutputTypeRepr.NEW_ROAD_CROSSINGS: OutputType.NEW_ROAD_CROSSINGS,
            OutputTypeRepr.RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY: OutputType.RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY,
            OutputTypeRepr.SCHOOL_STREETS: OutputType.SCHOOL_STREETS,
            OutputTypeRepr.UPGRADES_TO_EXISTING_FACILITIES: OutputType.UPGRADES_TO_EXISTING_FACILITIES,
            OutputTypeRepr.E_SCOOTER_TRIALS: OutputType.E_SCOOTER_TRIALS,
            OutputTypeRepr.PARK_AND_CYCLE_STRIDE_FACILITIES: OutputType.PARK_AND_CYCLE_STRIDE_FACILITIES,
            OutputTypeRepr.TRAFFIC_CALMING: OutputType.TRAFFIC_CALMING,
            OutputTypeRepr.WIDENING_EXISTING_FOOTWAY: OutputType.WIDENING_EXISTING_FOOTWAY,
            OutputTypeRepr.OTHER_INTERVENTIONS: OutputType.OTHER_INTERVENTIONS,
        }
        return members[self]


@unique
class OutputMeasureRepr(Enum):
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
        members = {
            OutputMeasureRepr.MILES: OutputMeasure.MILES,
            OutputMeasureRepr.NUMBER_OF_JUNCTIONS: OutputMeasure.NUMBER_OF_JUNCTIONS,
            OutputMeasureRepr.SIZE_OF_AREA: OutputMeasure.SIZE_OF_AREA,
            OutputMeasureRepr.NUMBER_OF_PARKING_SPACES: OutputMeasure.NUMBER_OF_PARKING_SPACES,
            OutputMeasureRepr.NUMBER_OF_CROSSINGS: OutputMeasure.NUMBER_OF_CROSSINGS,
            OutputMeasureRepr.NUMBER_OF_SCHOOL_STREETS: OutputMeasure.NUMBER_OF_SCHOOL_STREETS,
            OutputMeasureRepr.NUMBER_OF_TRIALS: OutputMeasure.NUMBER_OF_TRIALS,
            OutputMeasureRepr.NUMBER_OF_BUS_GATES: OutputMeasure.NUMBER_OF_BUS_GATES,
            OutputMeasureRepr.NUMBER_OF_UPGRADES: OutputMeasure.NUMBER_OF_UPGRADES,
            OutputMeasureRepr.NUMBER_OF_CHILDREN_AFFECTED: OutputMeasure.NUMBER_OF_CHILDREN_AFFECTED,
            OutputMeasureRepr.NUMBER_OF_MEASURES_PLANNED: OutputMeasure.NUMBER_OF_MEASURES_PLANNED,
        }
        return members[self]
