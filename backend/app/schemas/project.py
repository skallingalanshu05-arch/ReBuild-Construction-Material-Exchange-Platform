from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.project import ProjectStatus
from app.utils.object_id import PyObjectId


class ProjectCreate(BaseModel):
    project_name: str = Field(..., min_length=2, max_length=200)
    project_description: Optional[str] = None
    project_type: str = Field(..., min_length=2, max_length=100)
    address: str
    city: str
    state: str
    postal_code: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    project_status: ProjectStatus = ProjectStatus.PLANNED
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class ProjectUpdate(BaseModel):
    project_name: Optional[str] = Field(None, min_length=2, max_length=200)
    project_description: Optional[str] = None
    project_type: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    project_status: Optional[ProjectStatus] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class ProjectPublic(BaseModel):
    id: PyObjectId
    project_name: str
    company_id: PyObjectId
    project_description: Optional[str] = None
    project_type: str
    address: str
    city: str
    state: str
    postal_code: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    project_status: ProjectStatus
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    created_at: datetime
