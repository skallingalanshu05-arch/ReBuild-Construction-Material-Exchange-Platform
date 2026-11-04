import re
from datetime import datetime
from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field, field_validator

T = TypeVar("T")

PASSWORD_MIN_LENGTH = 8
PASSWORD_PATTERN = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$")


class MessageResponse(BaseModel):
    success: bool = True
    message: str


class PaginatedData(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int


def validate_password_strength(password: str) -> str:
    if len(password) < PASSWORD_MIN_LENGTH:
        raise ValueError(f"Password must be at least {PASSWORD_MIN_LENGTH} characters")
    if not PASSWORD_PATTERN.match(password):
        raise ValueError("Password must include upper, lower case letters and a digit")
    return password


class GeoPoint(BaseModel):
    type: str = "Point"
    coordinates: List[float] = Field(..., min_length=2, max_length=2)

    @field_validator("coordinates")
    @classmethod
    def validate_coords(cls, v: List[float]) -> List[float]:
        lon, lat = v[0], v[1]
        if not (-180 <= lon <= 180 and -90 <= lat <= 90):
            raise ValueError("Invalid longitude/latitude")
        return v


def utc_now() -> datetime:
    from datetime import timezone

    return datetime.now(timezone.utc)


def doc_timestamps() -> dict:
    now = utc_now()
    return {"created_at": now, "updated_at": now}
