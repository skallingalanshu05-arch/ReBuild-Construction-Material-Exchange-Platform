from fastapi import APIRouter, Depends

from app.core.exceptions import AppException
from app.core.permissions import require_admin
from app.database.connection import get_database
from app.schemas.common import doc_timestamps, utc_now
from app.utils.object_id import oid_to_str, str_to_object_id
from app.utils.response import success_data

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("")
async def list_categories(active_only: bool = True):
    db = get_database()
    query = {"is_active": True} if active_only else {}
    cursor = db.categories.find(query).sort("name", 1)
    items = [oid_to_str(c) async for c in cursor]
    return success_data(items)


@router.get("/{category_id}")
async def get_category(category_id: str):
    db = get_database()
    cat = await db.categories.find_one({"_id": str_to_object_id(category_id)})
    if not cat:
        raise AppException("Category not found", status_code=404)
    return success_data(oid_to_str(cat))


@router.post("")
async def admin_create_category(
    body: dict,
    _admin=Depends(require_admin),
):
    db = get_database()
    name = body.get("name")
    if not name:
        raise AppException("Category name is required")
    if await db.categories.find_one({"name": name}):
        raise AppException("Category name already exists", status_code=409)
    doc = {
        "name": name,
        "description": body.get("description"),
        "parent_category_id": body.get("parent_category_id"),
        "image_url": body.get("image_url"),
        "is_active": True,
        **doc_timestamps(),
    }
    result = await db.categories.insert_one(doc)
    created = await db.categories.find_one({"_id": result.inserted_id})
    return success_data(oid_to_str(created), "Category created")


@router.patch("/{category_id}")
async def admin_update_category(category_id: str, body: dict, _admin=Depends(require_admin)):
    db = get_database()
    updates = {k: v for k, v in body.items() if k in ("name", "description", "image_url", "parent_category_id")}
    if "name" in updates:
        dup = await db.categories.find_one({"name": updates["name"], "_id": {"$ne": str_to_object_id(category_id)}})
        if dup:
            raise AppException("Category name already exists", status_code=409)
    updates["updated_at"] = utc_now()
    result = await db.categories.update_one({"_id": str_to_object_id(category_id)}, {"$set": updates})
    if result.matched_count == 0:
        raise AppException("Category not found", status_code=404)
    cat = await db.categories.find_one({"_id": str_to_object_id(category_id)})
    return success_data(oid_to_str(cat), "Category updated")


@router.patch("/{category_id}/deactivate")
async def admin_deactivate_category(category_id: str, _admin=Depends(require_admin)):
    db = get_database()
    result = await db.categories.update_one(
        {"_id": str_to_object_id(category_id)},
        {"$set": {"is_active": False, "updated_at": utc_now()}},
    )
    if result.matched_count == 0:
        raise AppException("Category not found", status_code=404)
    return success_data(None, "Category deactivated")
