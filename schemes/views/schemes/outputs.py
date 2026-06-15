from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from itertools import groupby
from typing import Iterator, Self

from schemes.domain.schemes.observations import ObservationType
from schemes.domain.schemes.outputs import OutputMeasure, OutputRevision, OutputType


@dataclass(frozen=True)
class OutputTypeContext:
    name: str
    _NAMES = {
        OutputType.NEW_SEGREGATED_CYCLING_FACILITY: "New segregated cycling facility",
        OutputType.NEW_TEMPORARY_SEGREGATED_CYCLING_FACILITY: "New temporary segregated cycling facility",
        OutputType.NEW_JUNCTION_TREATMENT: "New junction treatment",
        OutputType.NEW_PERMANENT_FOOTWAY: "New permanent footway",
        OutputType.NEW_TEMPORARY_FOOTWAY: "New temporary footway",
        OutputType.NEW_SHARED_USE_WALKING_AND_CYCLING_FACILITIES: "New shared use (walking and cycling) facilities",
        OutputType.NEW_SHARED_USE_WALKING_WHEELING_AND_CYCLING_FACILITIES: "New shared use (walking, wheeling & cycling) facilities",
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


@dataclass(frozen=True)
class SchemeOutputRowContext:
    type: OutputTypeContext
    measure: OutputMeasureContext
    planned: Decimal | None


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
