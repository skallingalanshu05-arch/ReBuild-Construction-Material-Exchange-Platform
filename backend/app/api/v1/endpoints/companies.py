from fastapi import APIRouter, Depends, status

from app.core.exceptions import AppException
from app.core.permissions import get_current_user
from app.database.connection import get_database
from app.schemas.common import doc_timestamps, utc_now
from app.schemas.company import CompanyCreate, CompanyUpdate
from app.utils.object_id import oid_to_str, str_to_object_id
from app.utils.response import success_data, success_response

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_company(body: CompanyCreate, user=Depends(get_current_user)):
    if user.get("company_id"):
        raise AppException("User already belongs to a company", status_code=400)
    if not body.is_supplier and not body.is_buyer:
        raise AppException("Company must be a supplier and/or buyer", status_code=400)

    db = get_database()
    doc = body.model_dump()
    doc.update(doc_timestamps())
    doc["verification_status"] = "PENDING"
    result = await db.companies.insert_one(doc)
    company_id = str(result.inserted_id)
    await db.users.update_one(
        {"_id": str_to_object_id(user["id"])},
        {"$set": {"company_id": company_id, "updated_at": utc_now()}},
    )
    company = await db.companies.find_one({"_id": result.inserted_id})
    return success_response(oid_to_str(company), "Company created", status.HTTP_201_CREATED)


@router.get("/me")
async def get_my_company(user=Depends(get_current_user)):
    if not user.get("company_id"):
        raise AppException("No company associated with user", status_code=404)
    db = get_database()
    company = await db.companies.find_one({"_id": str_to_object_id(user["company_id"])})
    if not company:
        raise AppException("Company not found", status_code=404)
    return success_data(oid_to_str(company))


@router.patch("/me")
async def update_my_company(body: CompanyUpdate, user=Depends(get_current_user)):
    if not user.get("company_id"):
        raise AppException("No company associated with user", status_code=404)
    db = get_database()
    updates = body.model_dump(exclude_unset=True)
    if not updates:
        raise AppException("No fields to update")
    updates["updated_at"] = utc_now()
    await db.companies.update_one({"_id": str_to_object_id(user["company_id"])}, {"$set": updates})
    company = await db.companies.find_one({"_id": str_to_object_id(user["company_id"])})
    return success_data(oid_to_str(company), "Company updated")


@router.get("/{company_id}")
async def get_company(company_id: str, user=Depends(get_current_user)):
    db = get_database()
    company = await db.companies.find_one({"_id": str_to_object_id(company_id)})
    if not company:
        raise AppException("Company not found", status_code=404)
    return success_data(oid_to_str(company))
