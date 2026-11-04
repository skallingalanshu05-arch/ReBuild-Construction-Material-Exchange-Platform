from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.request import RequestStatus
from app.utils.object_id import PyObjectId


class MaterialRequestCreate(BaseModel):
    requirement_id: Optional[PyObjectId] = None
    material_id: PyObjectId
    requested_quantity: float = Field(..., gt=0)
    offered_price: float = Field(0, ge=0)
    message: Optional[str] = None


class MaterialRequestNegotiate(BaseModel):
    supplier_quoted_price: float = Field(..., ge=0)
    message: Optional[str] = None


class MaterialRequestCounterResponse(BaseModel):
    accept: bool
    message: Optional[str] = None


class MaterialRequestPublic(BaseModel):
    id: PyObjectId
    requirement_id: Optional[PyObjectId] = None
    material_id: PyObjectId
    buyer_company_id: PyObjectId
    supplier_company_id: PyObjectId
    requested_quantity: float
    offered_price: float
    supplier_quoted_price: Optional[float] = None
    message: Optional[str] = None
    request_status: RequestStatus
    status_history: list
    created_at: datetime
    updated_at: datetime
