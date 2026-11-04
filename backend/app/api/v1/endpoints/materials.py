from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_material_service
from app.core.exceptions import AppException
from app.core.permissions import get_current_user
from app.models.material import ListingStatus
from app.models.user import UserRole
from app.schemas.material import MaterialCreate, MaterialUpdate
from app.services.material_service import MaterialService
from app.utils.pagination import sort_param
from app.utils.response import success_data, success_response

router = APIRouter(prefix="/materials", tags=["Materials"])


def _require_supplier_company(user):
    if not user.get("company_id"):
        raise AppException("Create a company profile first", status_code=400)
    return user["company_id"]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_material(
    body: MaterialCreate,
    user=Depends(get_current_user),
    service: MaterialService = Depends(get_material_service),
):
    company_id = _require_supplier_company(user)
    data = await service.create(company_id, body.model_dump())
    return success_response(data, "Material registered successfully", status.HTTP_201_CREATED)


@router.get("")
async def search_materials(
    q: Optional[str] = None,
    category_id: Optional[str] = None,
    condition: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_quantity: Optional[float] = None,
    availability_type: Optional[str] = None,
    city: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: str = "desc",
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: MaterialService = Depends(get_material_service),
):
    field, direction = sort_param(sort_by, sort_order)
    filters = {
        "q": q,
        "category_id": category_id,
        "condition": condition,
        "min_price": min_price,
        "max_price": max_price,
        "min_quantity": min_quantity,
        "availability_type": availability_type,
        "city": city,
        "page": page,
        "page_size": page_size,
        "sort_field": field,
        "sort_dir": direction,
    }
    data = await service.search(filters)
    return success_data(data)


@router.get("/my-listings")
async def my_listings(
    user=Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: MaterialService = Depends(get_material_service),
):
    company_id = _require_supplier_company(user)
    field, direction = sort_param("created_at", "desc")
    data = await service.search(
        {"page": page, "page_size": page_size, "sort_field": field, "sort_dir": direction},
        company_id=company_id,
        own_only=True,
    )
    return success_data(data)


@router.get("/{material_id}")
async def get_material(material_id: str, service: MaterialService = Depends(get_material_service)):
    data = await service.get_by_id(material_id)
    return success_data(data)


@router.patch("/{material_id}")
async def update_material(
    material_id: str,
    body: MaterialUpdate,
    user=Depends(get_current_user),
    service: MaterialService = Depends(get_material_service),
):
    company_id = user.get("company_id")
    is_admin = user.get("role") == UserRole.ADMIN.value
    data = await service.update(
        material_id, company_id or "", body.model_dump(exclude_unset=True), is_admin=is_admin
    )
    return success_data(data, "Material updated")


@router.delete("/{material_id}")
async def delete_material(
    material_id: str,
    user=Depends(get_current_user),
    service: MaterialService = Depends(get_material_service),
):
    company_id = user.get("company_id")
    is_admin = user.get("role") == UserRole.ADMIN.value
    await service.delete_or_archive(material_id, company_id or "", is_admin=is_admin)
    return success_data(None, "Material archived")
