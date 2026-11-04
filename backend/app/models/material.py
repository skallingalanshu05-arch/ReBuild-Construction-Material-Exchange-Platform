from enum import Enum


class MaterialCondition(str, Enum):
    POOR = "POOR"
    FAIR = "FAIR"
    GOOD = "GOOD"
    EXCELLENT = "EXCELLENT"


class AvailabilityType(str, Enum):
    READY = "READY"
    WITHIN_7_DAYS = "WITHIN_7_DAYS"
    WITHIN_30_DAYS = "WITHIN_30_DAYS"
    CUSTOM_DATE = "CUSTOM_DATE"


class MeasurementUnit(str, Enum):
    PIECE = "PIECE"
    KG = "KG"
    TONNE = "TONNE"
    CUBIC_METER = "CUBIC_METER"
    CUBIC_FEET = "CUBIC_FEET"
    BAG = "BAG"
    SQUARE_METER = "SQUARE_METER"
    SQUARE_FEET = "SQUARE_FEET"
    LITRE = "LITRE"
    OTHER = "OTHER"


class ListingStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    RESERVED = "RESERVED"
    SOLD = "SOLD"
    EXPIRED = "EXPIRED"
    INACTIVE = "INACTIVE"


CONDITION_RANK = {
    MaterialCondition.POOR: 1,
    MaterialCondition.FAIR: 2,
    MaterialCondition.GOOD: 3,
    MaterialCondition.EXCELLENT: 4,
}
