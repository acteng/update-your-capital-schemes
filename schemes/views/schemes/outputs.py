from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum, unique
from itertools import groupby
from typing import Iterator, Self

from pydantic import BaseModel

from schemes.dicts import inverse_dict
from schemes.domain.dates import DateRange
from schemes.domain.schemes.observations import ObservationType
from schemes.domain.schemes.outputs import OutputMeasure, OutputRevision, OutputType, OutputTypeMeasure
from schemes.views.schemes.observations import ObservationTypeRepr


@dataclass(frozen=True)
class SchemeOutputsContext:
    outputs: list[SchemeOutputRowContext]

    @classmethod
    def from_domain(cls, output_revisions: list[OutputRevision]) -> Self:
        return cls(
            outputs=[
                SchemeOutputRowContext(
                    type=OutputTypeContext.from_domain(type_),
                    measure=OutputMeasureContext.from_domain(measure),
                    planned=cls._get_value(group, ObservationType.PLANNED),
                )
                for (type_, measure), group in groupby(
                    sorted(output_revisions, key=cls._by_type_and_measure), cls._by_type_and_measure
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
    def from_domain(cls, type_: OutputType) -> Self:
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
    def from_domain(cls, measure: OutputMeasure) -> Self:
        return cls(name=cls._NAMES[measure])


class OutputRevisionRepr(BaseModel):
    effective_date_from: str
    effective_date_to: str | None
    type: OutputTypeRepr
    measure: OutputMeasureRepr
    value: str
    observation_type: ObservationTypeRepr
    id: int | None = None

    @classmethod
    def from_domain(cls, output_revision: OutputRevision) -> Self:
        return cls(
            id=output_revision.id,
            effective_date_from=output_revision.effective.date_from.isoformat(),
            effective_date_to=(
                output_revision.effective.date_to.isoformat() if output_revision.effective.date_to else None
            ),
            type=OutputTypeRepr.from_domain(output_revision.type_measure.type),
            measure=OutputMeasureRepr.from_domain(output_revision.type_measure.measure),
            value=str(output_revision.value),
            observation_type=ObservationTypeRepr.from_domain(output_revision.observation_type),
        )

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
class OutputTypeRepr(str, Enum):
    NEW_SEGREGATED_CYCLING_FACILITY = "new segregated cycling facility"
    NEW_TEMPORARY_SEGREGATED_CYCLING_FACILITY = "new temporary segregated cycling facility"
    NEW_JUNCTION_TREATMENT = "new junction treatment"
    NEW_PERMANENT_FOOTWAY = "new permanent footway"
    NEW_TEMPORARY_FOOTWAY = "new temporary footway"
    NEW_SHARED_USE_FACILITIES = "new shared use (walking and cycling) facilities"
    NEW_SHARED_USE_FACILITIES_WHEELING = "new shared use (walking, wheeling & cycling) facilities"
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

    @classmethod
    def from_domain(cls, type_: OutputType) -> OutputTypeRepr:
        return cls._members()[type_]

    def to_domain(self) -> OutputType:
        return inverse_dict(self._members())[self]

    @staticmethod
    def _members() -> dict[OutputType, OutputTypeRepr]:
        return {
            OutputType.NEW_SEGREGATED_CYCLING_FACILITY: OutputTypeRepr.NEW_SEGREGATED_CYCLING_FACILITY,
            OutputType.NEW_TEMPORARY_SEGREGATED_CYCLING_FACILITY: OutputTypeRepr.NEW_TEMPORARY_SEGREGATED_CYCLING_FACILITY,
            OutputType.NEW_JUNCTION_TREATMENT: OutputTypeRepr.NEW_JUNCTION_TREATMENT,
            OutputType.NEW_PERMANENT_FOOTWAY: OutputTypeRepr.NEW_PERMANENT_FOOTWAY,
            OutputType.NEW_TEMPORARY_FOOTWAY: OutputTypeRepr.NEW_TEMPORARY_FOOTWAY,
            OutputType.NEW_SHARED_USE_FACILITIES: OutputTypeRepr.NEW_SHARED_USE_FACILITIES,
            OutputType.NEW_SHARED_USE_FACILITIES_WHEELING: OutputTypeRepr.NEW_SHARED_USE_FACILITIES_WHEELING,
            OutputType.IMPROVEMENTS_TO_EXISTING_ROUTE: OutputTypeRepr.IMPROVEMENTS_TO_EXISTING_ROUTE,
            OutputType.AREA_WIDE_TRAFFIC_MANAGEMENT: OutputTypeRepr.AREA_WIDE_TRAFFIC_MANAGEMENT,
            OutputType.BUS_PRIORITY_MEASURES: OutputTypeRepr.BUS_PRIORITY_MEASURES,
            OutputType.SECURE_CYCLE_PARKING: OutputTypeRepr.SECURE_CYCLE_PARKING,
            OutputType.NEW_ROAD_CROSSINGS: OutputTypeRepr.NEW_ROAD_CROSSINGS,
            OutputType.RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY: OutputTypeRepr.RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY,
            OutputType.SCHOOL_STREETS: OutputTypeRepr.SCHOOL_STREETS,
            OutputType.UPGRADES_TO_EXISTING_FACILITIES: OutputTypeRepr.UPGRADES_TO_EXISTING_FACILITIES,
            OutputType.E_SCOOTER_TRIALS: OutputTypeRepr.E_SCOOTER_TRIALS,
            OutputType.PARK_AND_CYCLE_STRIDE_FACILITIES: OutputTypeRepr.PARK_AND_CYCLE_STRIDE_FACILITIES,
            OutputType.TRAFFIC_CALMING: OutputTypeRepr.TRAFFIC_CALMING,
            OutputType.WIDENING_EXISTING_FOOTWAY: OutputTypeRepr.WIDENING_EXISTING_FOOTWAY,
            OutputType.OTHER_INTERVENTIONS: OutputTypeRepr.OTHER_INTERVENTIONS,
        }


@unique
class OutputMeasureRepr(str, Enum):
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

    @classmethod
    def from_domain(cls, measure: OutputMeasure) -> OutputMeasureRepr:
        return cls._members()[measure]

    def to_domain(self) -> OutputMeasure:
        return inverse_dict(self._members())[self]

    @staticmethod
    def _members() -> dict[OutputMeasure, OutputMeasureRepr]:
        return {
            OutputMeasure.MILES: OutputMeasureRepr.MILES,
            OutputMeasure.NUMBER_OF_JUNCTIONS: OutputMeasureRepr.NUMBER_OF_JUNCTIONS,
            OutputMeasure.SIZE_OF_AREA: OutputMeasureRepr.SIZE_OF_AREA,
            OutputMeasure.NUMBER_OF_PARKING_SPACES: OutputMeasureRepr.NUMBER_OF_PARKING_SPACES,
            OutputMeasure.NUMBER_OF_CROSSINGS: OutputMeasureRepr.NUMBER_OF_CROSSINGS,
            OutputMeasure.NUMBER_OF_SCHOOL_STREETS: OutputMeasureRepr.NUMBER_OF_SCHOOL_STREETS,
            OutputMeasure.NUMBER_OF_TRIALS: OutputMeasureRepr.NUMBER_OF_TRIALS,
            OutputMeasure.NUMBER_OF_BUS_GATES: OutputMeasureRepr.NUMBER_OF_BUS_GATES,
            OutputMeasure.NUMBER_OF_UPGRADES: OutputMeasureRepr.NUMBER_OF_UPGRADES,
            OutputMeasure.NUMBER_OF_CHILDREN_AFFECTED: OutputMeasureRepr.NUMBER_OF_CHILDREN_AFFECTED,
            OutputMeasure.NUMBER_OF_MEASURES_PLANNED: OutputMeasureRepr.NUMBER_OF_MEASURES_PLANNED,
        }
