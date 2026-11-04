from typing import Optional

from pydantic import BaseModel

from app.models.match import CompatibilityLabel, MatchType
from app.models.material import AvailabilityType, MaterialCondition, MeasurementUnit
from app.utils.object_id import PyObjectId


class ScoreBreakdown(BaseModel):
    material_type: float
    quantity: float
    condition: float
    location: float
    availability: float


class MatchResult(BaseModel):
    material_id: PyObjectId
    supplier_company_id: PyObjectId
    material_title: str
    available_quantity: float
    required_quantity: float
    unit: MeasurementUnit
    material_condition: MaterialCondition
    location: str
    distance_km: Optional[float] = None
    location_approximate: bool = False
    availability_type: AvailabilityType
    expected_price: float
    matching_score: float
    match_type: MatchType
    compatibility_label: CompatibilityLabel
    score_breakdown: ScoreBreakdown


class MatchQueryParams(BaseModel):
    sort_by: str = "matching_score"
    sort_order: str = "desc"
    min_score: Optional[float] = None
