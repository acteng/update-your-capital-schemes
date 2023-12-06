from enum import Enum, auto, unique


@unique
class ObservationType(Enum):
    PLANNED = auto()
    ACTUAL = auto()
