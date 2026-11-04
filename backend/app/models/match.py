from enum import Enum


class MatchType(str, Enum):
    FULL_MATCH = "FULL_MATCH"
    PARTIAL_MATCH = "PARTIAL_MATCH"


class CompatibilityLabel(str, Enum):
    HIGHLY_SUITABLE = "HIGHLY_SUITABLE"
    MODERATELY_SUITABLE = "MODERATELY_SUITABLE"
    LOW_SUITABILITY = "LOW_SUITABILITY"
