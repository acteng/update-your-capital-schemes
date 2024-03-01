from enum import Enum, auto, unique


@unique
class DataSource(Enum):
    PULSE_5 = auto()
    PULSE_6 = auto()
    ATF4_BID = auto()
    ATF3_BID = auto()
    INSPECTORATE_REVIEW = auto()
    REGIONAL_MANAGER_REQUEST = auto()
    INVESTMENT_TEAM_REQUEST = auto()
    ATE_PUBLISHED_DATA = auto()
    CHANGE_CONTROL = auto()
    ATF4E_BID = auto()
    ATF4E_MODERATION = auto()
    PULSE_2023_24_Q2 = auto()
    PULSE_2023_24_Q3 = auto()
    PULSE_2023_24_Q4 = auto()
    INITIAL_SCHEME_LIST = auto()
    AUTHORITY_UPDATE = auto()
    PULSE_2023_24_Q2_DATA_CLEANSE = auto()
