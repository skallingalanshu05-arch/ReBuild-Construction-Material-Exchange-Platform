from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models.company import VerificationStatus
from app.utils.object_id import PyObjectId


class CompanyCreate(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=200)
    registration_number: Optional[str] = None
    business_email: EmailStr
    phone_number: str = Field(..., min_length=8, max_length=20)
    address: str
    city: str
    state: str
    country: str
    postal_code: str
    company_description: Optional[str] = None
    logo_url: Optional[str] = None
    is_supplier: bool = False
    is_buyer: bool = False


class CompanyUpdate(BaseModel):
    company_name: Optional[str] = Field(None, min_length=2, max_length=200)
    registration_number: Optional[str] = None
    business_email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, min_length=8, max_length=20)
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    company_description: Optional[str] = None
    logo_url: Optional[str] = None
    is_supplier: Optional[bool] = None
    is_buyer: Optional[bool] = None


class CompanyPublic(BaseModel):
    id: PyObjectId
    company_name: str
    registration_number: Optional[str] = None
    business_email: EmailStr
    phone_number: str
    address: str
    city: str
    state: str
    country: str
    postal_code: str
    company_description: Optional[str] = None
    logo_url: Optional[str] = None
    is_supplier: bool
    is_buyer: bool
    verification_status: VerificationStatus
    created_at: datetime
    updated_at: datetime
