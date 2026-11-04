from fastapi import APIRouter, Depends, Query

from app.api.deps import get_request_service
from app.core.exceptions import AppException
from app.core.permissions import get_current_user
from app.schemas.request import MaterialRequestCreate, MaterialRequestCounterResponse, MaterialRequestNegotiate
from app.services.request_service import RequestService
from app.utils.response import success_data

router = APIRouter(prefix="/requests", tags=["Requests"])


def _require_company(user):
    if not user.get("company_id"):
        raise AppException("Create a company profile first", status_code=400)
    return user["company_id"]


@router.post("")
async def create_request(
    body: MaterialRequestCreate,
    user=Depends(get_current_user),
    service: RequestService = Depends(get_request_service),
):
    company_id = _require_company(user)
    data = await service.create_request(company_id, user["id"], body.model_dump())
    return success_data(data, "Request sent")


@router.get("")
async def list_requests(
    user=Depends(get_current_user),
    role: str = Query("all", pattern="^(all|buyer|supplier)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: RequestService = Depends(get_request_service),
):
    company_id = _require_company(user)
    data = await service.list_requests(company_id, role=role, page=page, page_size=page_size)
    return success_data(data)


@router.get("/{request_id}")
async def get_request(
    request_id: str,
    user=Depends(get_current_user),
    service: RequestService = Depends(get_request_service),
):
    doc = await service._get_request(request_id)
    company_id = _require_company(user)
    service._ensure_party(doc, company_id)
    from app.utils.object_id import oid_to_str

    return success_data(oid_to_str(doc))


@router.patch("/{request_id}/accept")
async def accept_request(
    request_id: str,
    user=Depends(get_current_user),
    service: RequestService = Depends(get_request_service),
):
    company_id = _require_company(user)
    data = await service.accept(request_id, company_id)
    return success_data(data, "Request accepted")


@router.patch("/{request_id}/reject")
async def reject_request(
    request_id: str,
    user=Depends(get_current_user),
    service: RequestService = Depends(get_request_service),
):
    company_id = _require_company(user)
    data = await service.reject(request_id, company_id)
    return success_data(data, "Request rejected")


@router.patch("/{request_id}/negotiate")
async def negotiate_request(
    request_id: str,
    body: MaterialRequestNegotiate,
    user=Depends(get_current_user),
    service: RequestService = Depends(get_request_service),
):
    company_id = _require_company(user)
    data = await service.negotiate(request_id, company_id, body.supplier_quoted_price, body.message)
    return success_data(data, "Counter offer sent")


@router.patch("/{request_id}/counter-response")
async def counter_response(
    request_id: str,
    body: MaterialRequestCounterResponse,
    user=Depends(get_current_user),
    service: RequestService = Depends(get_request_service),
):
    company_id = _require_company(user)
    data = await service.buyer_counter_response(request_id, company_id, body.accept)
    return success_data(data, "Counter offer processed")


@router.patch("/{request_id}/confirm")
async def confirm_request(
    request_id: str,
    user=Depends(get_current_user),
    service: RequestService = Depends(get_request_service),
):
    company_id = _require_company(user)
    data = await service.confirm(request_id, company_id)
    return success_data(data, "Request confirmed")


@router.patch("/{request_id}/cancel")
async def cancel_request(
    request_id: str,
    user=Depends(get_current_user),
    service: RequestService = Depends(get_request_service),
):
    company_id = _require_company(user)
    data = await service.cancel(request_id, company_id)
    return success_data(data, "Request cancelled")
