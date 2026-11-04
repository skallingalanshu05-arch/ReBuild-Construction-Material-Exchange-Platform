from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.material import MaterialCondition, MeasurementUnit
from app.models.requirement import RequirementStatus
from app.utils.object_id import PyObjectId


class RequirementCreate(BaseModel):
    requirement_title: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    project_id: Optional[PyObjectId] = None
    category_id: PyObjectId
    material_type: str = Field(..., min_length=1, max_length=120)
    required_quantity: float = Field(..., gt=0)
    unit: MeasurementUnit
    minimum_acceptable_condition: MaterialCondition
    allow_lower_quality: bool = False
    maximum_budget: Optional[float] = Field(None, ge=0)
    preferred_location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    maximum_distance_km: Optional[float] = Field(None, gt=0)
    required_availability_date: date
    requirement_status: RequirementStatus = RequirementStatus.DRAFT


class RequirementUpdate(BaseModel):
    requirement_title: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = None
    project_id: Optional[PyObjectId] = None
    category_id: Optional[PyObjectId] = None
    material_type: Optional[str] = None
    required_quantity: Optional[float] = Field(None, gt=0)
    unit: Optional[MeasurementUnit] = None
    minimum_acceptable_condition: Optional[MaterialCondition] = None
    allow_lower_quality: Optional[bool] = None
    maximum_budget: Optional[float] = Field(None, ge=0)
    preferred_location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    maximum_distance_km: Optional[float] = Field(None, gt=0)
    required_availability_date: Optional[date] = None
    requirement_status: Optional[RequirementStatus] = None


class RequirementPublic(BaseModel):
    id: PyObjectId
    requirement_title: str
    description: Optional[str] = None
    company_id: PyObjectId
    project_id: Optional[PyObjectId] = None
    category_id: PyObjectId
    material_type: str
    required_quantity: float
    unit: MeasurementUnit
    minimum_acceptable_condition: MaterialCondition
    allow_lower_quality: bool
    maximum_budget: Optional[float] = None
    preferred_location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    maximum_distance_km: Optional[float] = None
    required_availability_date: date
    requirement_status: RequirementStatus
    created_at: datetime
    updated_at: datetime
