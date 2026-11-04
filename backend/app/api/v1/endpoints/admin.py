from fastapi import APIRouter, Depends, Query

from app.core.exceptions import AppException
from app.core.permissions import require_admin
from app.database.connection import get_database
from app.models.material import ListingStatus
from app.models.requirement import RequirementStatus
from app.models.transaction import TransactionStatus
from app.schemas.common import utc_now
from app.services.auth_service import AuthService
from app.utils.object_id import oid_to_str, str_to_object_id
from app.utils.pagination import paginated_meta, pagination_params
from app.utils.response import success_data

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard")
async def dashboard(_admin=Depends(require_admin)):
    db = get_database()
    stats = {
        "total_users": await db.users.count_documents({}),
        "total_companies": await db.companies.count_documents({}),
        "total_suppliers": await db.companies.count_documents({"is_supplier": True}),
        "total_buyers": await db.companies.count_documents({"is_buyer": True}),
        "total_projects": await db.projects.count_documents({}),
        "total_active_materials": await db.materials.count_documents(
            {"listing_status": ListingStatus.ACTIVE.value}
        ),
        "total_requirements": await db.requirements.count_documents({}),
        "total_requests": await db.requests.count_documents({}),
        "total_completed_transactions": await db.transactions.count_documents(
            {"transaction_status": TransactionStatus.COMPLETED.value}
        ),
    }
    pipeline = [
        {"$match": {"transaction_status": TransactionStatus.COMPLETED.value}},
        {"$group": {"_id": None, "total_quantity": {"$sum": "$quantity"}}},
    ]
    agg = await db.transactions.aggregate(pipeline).to_list(1)
    stats["total_quantity_exchanged"] = agg[0]["total_quantity"] if agg else 0
    return success_data(stats)


@router.get("/users")
async def list_users(
    _admin=Depends(require_admin),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    db = get_database()
    pg = pagination_params(page, page_size)
    total = await db.users.count_documents({})
    cursor = db.users.find({}, {"password_hash": 0}).sort("created_at", -1).skip(pg["skip"]).limit(pg["limit"])
    items = [oid_to_str(u) async for u in cursor]
    return success_data({"items": items, **paginated_meta(total, pg["page"], pg["page_size"])})


@router.patch("/users/{user_id}/activate")
async def activate_user(user_id: str, is_active: bool = True, _admin=Depends(require_admin)):
    auth = AuthService(get_database())
    user = await auth.set_user_active(user_id, is_active)
    return success_data(user, "User status updated")


@router.get("/companies")
async def list_companies(_admin=Depends(require_admin), page: int = 1, page_size: int = 20):
    db = get_database()
    pg = pagination_params(page, page_size)
    total = await db.companies.count_documents({})
    cursor = db.companies.find().sort("created_at", -1).skip(pg["skip"]).limit(pg["limit"])
    items = [oid_to_str(c) async for c in cursor]
    return success_data({"items": items, **paginated_meta(total, pg["page"], pg["page_size"])})


@router.patch("/companies/{company_id}/verify")
async def verify_company(company_id: str, status_value: str = Query(..., alias="status"), _admin=Depends(require_admin)):
    if status_value not in ("VERIFIED", "REJECTED", "PENDING"):
        raise AppException("Invalid verification status")
    db = get_database()
    result = await db.companies.update_one(
        {"_id": str_to_object_id(company_id)},
        {"$set": {"verification_status": status_value, "updated_at": utc_now()}},
    )
    if result.matched_count == 0:
        raise AppException("Company not found", status_code=404)
    company = await db.companies.find_one({"_id": str_to_object_id(company_id)})
    return success_data(oid_to_str(company), "Company verification updated")


@router.get("/materials")
async def admin_materials(_admin=Depends(require_admin), page: int = 1, page_size: int = 20):
    db = get_database()
    pg = pagination_params(page, page_size)
    total = await db.materials.count_documents({})
    cursor = db.materials.find().sort("created_at", -1).skip(pg["skip"]).limit(pg["limit"])
    items = [oid_to_str(m) async for m in cursor]
    return success_data({"items": items, **paginated_meta(total, pg["page"], pg["page_size"])})


@router.get("/requests")
async def admin_requests(_admin=Depends(require_admin), page: int = 1, page_size: int = 20):
    db = get_database()
    pg = pagination_params(page, page_size)
    total = await db.requests.count_documents({})
    cursor = db.requests.find().sort("created_at", -1).skip(pg["skip"]).limit(pg["limit"])
    items = [oid_to_str(r) async for r in cursor]
    return success_data({"items": items, **paginated_meta(total, pg["page"], pg["page_size"])})


@router.get("/transactions")
async def admin_transactions(_admin=Depends(require_admin), page: int = 1, page_size: int = 20):
    db = get_database()
    pg = pagination_params(page, page_size)
    total = await db.transactions.count_documents({})
    cursor = db.transactions.find().sort("created_at", -1).skip(pg["skip"]).limit(pg["limit"])
    items = [oid_to_str(t) async for t in cursor]
    return success_data({"items": items, **paginated_meta(total, pg["page"], pg["page_size"])})


@router.get("/requirements")
async def admin_requirements(_admin=Depends(require_admin), page: int = 1, page_size: int = 20):
    db = get_database()
    pg = pagination_params(page, page_size)
    total = await db.requirements.count_documents({})
    cursor = db.requirements.find().sort("created_at", -1).skip(pg["skip"]).limit(pg["limit"])
    items = [oid_to_str(r) async for r in cursor]
    return success_data({"items": items, **paginated_meta(total, pg["page"], pg["page_size"])})
