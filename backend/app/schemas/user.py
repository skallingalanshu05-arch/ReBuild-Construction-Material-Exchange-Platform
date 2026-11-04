from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models.user import AccountStatus, UserRole
from app.utils.object_id import PyObjectId


class UserPublic(BaseModel):
    id: PyObjectId
    full_name: str
    email: EmailStr
    mobile_number: str
    company_id: Optional[PyObjectId] = None
    role: UserRole
    account_status: AccountStatus
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=120)
    mobile_number: Optional[str] = Field(None, min_length=8, max_length=20)
