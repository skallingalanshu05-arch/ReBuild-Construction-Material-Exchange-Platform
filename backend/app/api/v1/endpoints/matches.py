from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_matching_service
from app.core.exceptions import AppException
from app.core.permissions import get_current_user
from app.database.connection import get_database
from app.models.material import ListingStatus
from app.models.requirement import RequirementStatus
from app.services.matching_service import MatchingService
from app.utils.object_id import str_to_object_id
from app.utils.response import success_data

router = APIRouter(prefix="/matches", tags=["Matching"])


@router.get("/requirement/{requirement_id}")
async def matches_for_requirement(
    requirement_id: str,
    user=Depends(get_current_user),
    sort_by: str = Query("matching_score"),
    sort_order: str = Query("desc"),
    min_score: Optional[float] = None,
    matching: MatchingService = Depends(get_matching_service),
):
    db = get_database()
    req = await db.requirements.find_one({"_id": str_to_object_id(requirement_id)})
    if not req:
        raise AppException("Requirement not found", status_code=404)
    if str(req.get("company_id")) != str(user.get("company_id")):
        raise AppException("Not authorized", status_code=403)
    materials = await db.materials.find({"listing_status": ListingStatus.ACTIVE.value}).to_list(
        length=5000
    )
    results = matching.match_requirement_to_materials(
        req, materials, sort_by=sort_by, sort_order=sort_order, min_score=min_score
    )
    return success_data(results)


@router.get("/material/{material_id}")
async def matches_for_material(
    material_id: str,
    user=Depends(get_current_user),
    sort_by: str = Query("matching_score"),
    sort_order: str = Query("desc"),
    min_score: Optional[float] = None,
    matching: MatchingService = Depends(get_matching_service),
):
    db = get_database()
    material = await db.materials.find_one({"_id": str_to_object_id(material_id)})
    if not material:
        raise AppException("Material not found", status_code=404)
    if str(material.get("company_id")) != str(user.get("company_id")):
        raise AppException("Not authorized", status_code=403)
    requirements = await db.requirements.find(
        {"requirement_status": RequirementStatus.ACTIVE.value}
    ).to_list(length=5000)
    results = matching.match_material_to_requirements(
        material, requirements, sort_by=sort_by, sort_order=sort_order, min_score=min_score
    )
    return success_data(results)
