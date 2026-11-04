from fastapi import APIRouter, Depends, Query

from app.core.exceptions import AppException
from app.core.permissions import get_current_user
from app.database.connection import get_database
from app.models.material import ListingStatus
from app.models.transaction import TransactionStatus
from app.schemas.common import utc_now
from app.utils.object_id import oid_to_str, str_to_object_id
from app.utils.pagination import paginated_meta, pagination_params
from app.utils.response import success_data

router = APIRouter(prefix="/transactions", tags=["Transactions"])


def _require_company(user):
    if not user.get("company_id"):
        raise AppException("Create a company profile first", status_code=400)
    return user["company_id"]


@router.get("")
async def list_transactions(
    user=Depends(get_current_user),
    role: str = Query("all", pattern="^(all|buyer|supplier)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    company_id = _require_company(user)
    db = get_database()
    pg = pagination_params(page, page_size)
    if role == "buyer":
        query = {"buyer_company_id": company_id}
    elif role == "supplier":
        query = {"supplier_company_id": company_id}
    else:
        query = {
            "$or": [{"buyer_company_id": company_id}, {"supplier_company_id": company_id}]
        }
    total = await db.transactions.count_documents(query)
    cursor = db.transactions.find(query).sort("created_at", -1).skip(pg["skip"]).limit(pg["limit"])
    items = [oid_to_str(t) async for t in cursor]
    return success_data({"items": items, **paginated_meta(total, pg["page"], pg["page_size"])})


@router.get("/{transaction_id}")
async def get_transaction(transaction_id: str, user=Depends(get_current_user)):
    company_id = _require_company(user)
    db = get_database()
    tx = await db.transactions.find_one({"_id": str_to_object_id(transaction_id)})
    if not tx:
        raise AppException("Transaction not found", status_code=404)
    if company_id not in (str(tx.get("buyer_company_id")), str(tx.get("supplier_company_id"))):
        raise AppException("Not authorized", status_code=403)
    return success_data(oid_to_str(tx))


@router.patch("/{transaction_id}/complete")
async def complete_transaction(transaction_id: str, user=Depends(get_current_user)):
    company_id = _require_company(user)
    db = get_database()
    tx = await db.transactions.find_one({"_id": str_to_object_id(transaction_id)})
    if not tx:
        raise AppException("Transaction not found", status_code=404)
    if company_id not in (str(tx.get("buyer_company_id")), str(tx.get("supplier_company_id"))):
        raise AppException("Not authorized", status_code=403)

    material = await db.materials.find_one({"_id": str_to_object_id(tx["material_id"])})
    qty = float(tx["quantity"])
    if material:
        new_available = float(material["available_quantity"]) - qty
        new_reserved = max(float(material.get("reserved_quantity", 0)) - qty, 0)
        listing_status = material.get("listing_status")
        if new_available <= 0:
            listing_status = ListingStatus.SOLD.value
        await db.materials.update_one(
            {"_id": material["_id"]},
            {
                "$set": {
                    "available_quantity": max(new_available, 0),
                    "reserved_quantity": new_reserved,
                    "listing_status": listing_status,
                    "updated_at": utc_now(),
                }
            },
        )

    await db.transactions.update_one(
        {"_id": tx["_id"]},
        {
            "$set": {
                "transaction_status": TransactionStatus.COMPLETED.value,
                "completed_date": utc_now(),
                "updated_at": utc_now(),
            }
        },
    )
    req = await db.requests.find_one({"_id": str_to_object_id(tx["request_id"])})
    if req:
        from app.services.request_service import RequestService

        await RequestService(db).complete_request(str(req["_id"]))

    updated = await db.transactions.find_one({"_id": tx["_id"]})
    return success_data(oid_to_str(updated), "Transaction completed")
