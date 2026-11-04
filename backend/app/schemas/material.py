from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.models.material import (
    AvailabilityType,
    ListingStatus,
    MaterialCondition,
    MeasurementUnit,
)
from app.utils.object_id import PyObjectId


class MaterialCreate(BaseModel):
    material_title: str = Field(..., min_length=2, max_length=200)
    material_description: Optional[str] = None
    category_id: PyObjectId
    material_type: str = Field(..., min_length=1, max_length=120)
    project_id: Optional[PyObjectId] = None
    available_quantity: float = Field(..., gt=0)
    unit: MeasurementUnit
    material_condition: MaterialCondition
    expected_price: float = Field(0, ge=0)
    is_free_material: bool = False
    currency: str = "INR"
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    availability_date: Optional[date] = None
    availability_type: AvailabilityType
    material_images: List[str] = Field(default_factory=list)
    listing_status: ListingStatus = ListingStatus.DRAFT


class MaterialUpdate(BaseModel):
    material_title: Optional[str] = Field(None, min_length=2, max_length=200)
    material_description: Optional[str] = None
    category_id: Optional[PyObjectId] = None
    material_type: Optional[str] = None
    project_id: Optional[PyObjectId] = None
    available_quantity: Optional[float] = Field(None, gt=0)
    unit: Optional[MeasurementUnit] = None
    material_condition: Optional[MaterialCondition] = None
    expected_price: Optional[float] = Field(None, ge=0)
    is_free_material: Optional[bool] = None
    currency: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    availability_date: Optional[date] = None
    availability_type: Optional[AvailabilityType] = None
    material_images: Optional[List[str]] = None
    listing_status: Optional[ListingStatus] = None


class MaterialPublic(BaseModel):
    id: PyObjectId
    material_title: str
    material_description: Optional[str] = None
    category_id: PyObjectId
    material_type: str
    company_id: PyObjectId
    project_id: Optional[PyObjectId] = None
    available_quantity: float
    reserved_quantity: float = 0
    unit: MeasurementUnit
    material_condition: MaterialCondition
    expected_price: float
    is_free_material: bool
    currency: str
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    availability_date: Optional[date] = None
    availability_type: AvailabilityType
    material_images: List[str]
    listing_status: ListingStatus
    created_at: datetime
    updated_at: datetime


class MaterialSearchParams(BaseModel):
    q: Optional[str] = None
    category_id: Optional[str] = None
    condition: Optional[MaterialCondition] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_quantity: Optional[float] = None
    availability_type: Optional[AvailabilityType] = None
    city: Optional[str] = None
    sort_by: Optional[str] = None
    sort_order: str = "desc"
    page: int = 1
    page_size: int = 20
