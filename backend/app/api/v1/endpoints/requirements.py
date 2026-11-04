from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.core.exceptions import AppException
from app.core.permissions import get_current_user
from app.database.connection import get_database
from app.models.requirement import RequirementStatus
from app.models.user import UserRole
from datetime import date, datetime, timezone

from app.schemas.common import doc_timestamps, utc_now


def _mongo_date(value: date) -> datetime:
    return datetime(value.year, value.month, value.day, tzinfo=timezone.utc)
from app.schemas.requirement import RequirementCreate, RequirementUpdate
from app.utils.object_id import oid_to_str, str_to_object_id
from app.utils.pagination import paginated_meta, pagination_params
from app.utils.response import success_data, success_response

router = APIRouter(prefix="/requirements", tags=["Requirements"])


def _require_company(user):
    if not user.get("company_id"):
        raise AppException("Create a company profile first", status_code=400)
    return user["company_id"]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_requirement(body: RequirementCreate, user=Depends(get_current_user)):
    company_id = _require_company(user)
    db = get_database()
    cat = await db.categories.find_one({"_id": str_to_object_id(body.category_id), "is_active": True})
    if not cat:
        raise AppException("Invalid category", status_code=400)
    doc = body.model_dump()
    for key in ("unit", "minimum_acceptable_condition", "requirement_status"):
        if hasattr(doc[key], "value"):
            doc[key] = doc[key].value
    doc["company_id"] = company_id
    doc["preferred_location_text"] = doc.pop("preferred_location")
    lat, lon = doc.get("latitude"), doc.get("longitude")
    doc["geo"] = (
        {"type": "Point", "coordinates": [lon, lat]} if lat is not None and lon is not None else None
    )
    doc["preferred_location"] = doc["preferred_location_text"]
    if isinstance(doc.get("required_availability_date"), date):
        doc["required_availability_date"] = _mongo_date(doc["required_availability_date"])
    if doc.get("project_id"):
        project = await db.projects.find_one(
            {"_id": str_to_object_id(doc["project_id"]), "company_id": company_id}
        )
        if not project:
            raise AppException("Invalid project", status_code=400)
    doc.update(doc_timestamps())
    result = await db.requirements.insert_one(doc)
    created = await db.requirements.find_one({"_id": result.inserted_id})
    return success_response(oid_to_str(created), "Requirement created", status.HTTP_201_CREATED)


@router.get("")
async def search_requirements(
    status_filter: Optional[str] = Query(None, alias="status"),
    category_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    db = get_database()
    query = {"requirement_status": RequirementStatus.ACTIVE.value}
    if status_filter:
        query["requirement_status"] = status_filter
    if category_id:
        query["category_id"] = category_id
    pg = pagination_params(page, page_size)
    total = await db.requirements.count_documents(query)
    cursor = db.requirements.find(query).sort("created_at", -1).skip(pg["skip"]).limit(pg["limit"])
    items = [oid_to_str(r) async for r in cursor]
    return success_data({"items": items, **paginated_meta(total, pg["page"], pg["page_size"])})


@router.get("/my-requirements")
async def my_requirements(
    user=Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    company_id = _require_company(user)
    db = get_database()
    pg = pagination_params(page, page_size)
    query = {"company_id": company_id}
    total = await db.requirements.count_documents(query)
    cursor = db.requirements.find(query).sort("created_at", -1).skip(pg["skip"]).limit(pg["limit"])
    items = [oid_to_str(r) async for r in cursor]
    return success_data({"items": items, **paginated_meta(total, pg["page"], pg["page_size"])})


@router.get("/{requirement_id}")
async def get_requirement(requirement_id: str, user=Depends(get_current_user)):
    db = get_database()
    req = await db.requirements.find_one({"_id": str_to_object_id(requirement_id)})
    if not req:
        raise AppException("Requirement not found", status_code=404)
    if str(req.get("company_id")) != str(user.get("company_id")) and user.get("role") != UserRole.ADMIN.value:
        if req.get("requirement_status") != RequirementStatus.ACTIVE.value:
            raise AppException("Not authorized", status_code=403)
    return success_data(oid_to_str(req))


@router.patch("/{requirement_id}")
async def update_requirement(
    requirement_id: str, body: RequirementUpdate, user=Depends(get_current_user)
):
    company_id = _require_company(user)
    db = get_database()
    req = await db.requirements.find_one(
        {"_id": str_to_object_id(requirement_id), "company_id": company_id}
    )
    if not req:
        raise AppException("Requirement not found", status_code=404)
    updates = body.model_dump(exclude_unset=True)
    for key in ("unit", "minimum_acceptable_condition", "requirement_status"):
        if key in updates and hasattr(updates[key], "value"):
            updates[key] = updates[key].value
    updates["updated_at"] = utc_now()
    await db.requirements.update_one({"_id": req["_id"]}, {"$set": updates})
    updated = await db.requirements.find_one({"_id": req["_id"]})
    return success_data(oid_to_str(updated), "Requirement updated")


@router.delete("/{requirement_id}")
async def delete_requirement(requirement_id: str, user=Depends(get_current_user)):
    company_id = _require_company(user)
    db = get_database()
    req = await db.requirements.find_one(
        {"_id": str_to_object_id(requirement_id), "company_id": company_id}
    )
    if not req:
        raise AppException("Requirement not found", status_code=404)
    await db.requirements.update_one(
        {"_id": req["_id"]},
        {"$set": {"requirement_status": RequirementStatus.CLOSED.value, "updated_at": utc_now()}},
    )
    return success_data(None, "Requirement closed")
