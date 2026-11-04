from fastapi import APIRouter, Depends, Query, status

from app.core.exceptions import AppException
from app.core.permissions import get_current_user
from app.database.connection import get_database
from app.models.project import ProjectStatus
from app.schemas.common import doc_timestamps, utc_now
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.utils.object_id import oid_to_str, str_to_object_id
from app.utils.pagination import paginated_meta, pagination_params
from app.utils.response import success_data, success_response

router = APIRouter(prefix="/projects", tags=["Projects"])


def _require_company(user):
    if not user.get("company_id"):
        raise AppException("Create a company profile first", status_code=400)
    return user["company_id"]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_project(body: ProjectCreate, user=Depends(get_current_user)):
    company_id = _require_company(user)
    db = get_database()
    doc = body.model_dump()
    doc["company_id"] = company_id
    doc.update(doc_timestamps())
    result = await db.projects.insert_one(doc)
    project = await db.projects.find_one({"_id": result.inserted_id})
    return success_response(oid_to_str(project), "Project created", status.HTTP_201_CREATED)


@router.get("")
async def list_projects(
    user=Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    company_id = _require_company(user)
    db = get_database()
    pg = pagination_params(page, page_size)
    query = {"company_id": company_id, "project_status": {"$ne": ProjectStatus.ARCHIVED.value}}
    total = await db.projects.count_documents(query)
    cursor = db.projects.find(query).sort("created_at", -1).skip(pg["skip"]).limit(pg["limit"])
    items = [oid_to_str(p) async for p in cursor]
    return success_data({"items": items, **paginated_meta(total, pg["page"], pg["page_size"])})


@router.get("/{project_id}")
async def get_project(project_id: str, user=Depends(get_current_user)):
    db = get_database()
    project = await db.projects.find_one({"_id": str_to_object_id(project_id)})
    if not project:
        raise AppException("Project not found", status_code=404)
    if str(project.get("company_id")) != str(user.get("company_id")) and user.get("role") != "ADMIN":
        raise AppException("Not authorized", status_code=403)
    return success_data(oid_to_str(project))


@router.patch("/{project_id}")
async def update_project(project_id: str, body: ProjectUpdate, user=Depends(get_current_user)):
    company_id = _require_company(user)
    db = get_database()
    project = await db.projects.find_one({"_id": str_to_object_id(project_id), "company_id": company_id})
    if not project:
        raise AppException("Project not found", status_code=404)
    updates = body.model_dump(exclude_unset=True)
    if updates:
        updates["updated_at"] = utc_now()
        await db.projects.update_one({"_id": project["_id"]}, {"$set": updates})
    updated = await db.projects.find_one({"_id": project["_id"]})
    return success_data(oid_to_str(updated), "Project updated")


@router.delete("/{project_id}")
async def delete_project(project_id: str, user=Depends(get_current_user)):
    company_id = _require_company(user)
    db = get_database()
    project = await db.projects.find_one({"_id": str_to_object_id(project_id), "company_id": company_id})
    if not project:
        raise AppException("Project not found", status_code=404)
    await db.projects.update_one(
        {"_id": project["_id"]},
        {"$set": {"project_status": ProjectStatus.ARCHIVED.value, "updated_at": utc_now()}},
    )
    return success_data(None, "Project archived")
