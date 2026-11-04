import math
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

from app.models.match import CompatibilityLabel, MatchType
from app.models.material import (
    CONDITION_RANK,
    AvailabilityType,
    ListingStatus,
    MaterialCondition,
)


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def _normalize_type(value: str) -> str:
    return "".join(value.lower().split())


def material_type_score(req_type: str, mat_type: str, same_category: bool) -> float:
    if _normalize_type(req_type) == _normalize_type(mat_type):
        return 30.0
    if same_category:
        return 15.0
    return 0.0


def quantity_score(available: float, required: float) -> tuple[float, MatchType]:
    if required <= 0:
        return 0.0, MatchType.PARTIAL_MATCH
    ratio = min(available / required, 1.0)
    score = ratio * 25.0
    match_type = MatchType.FULL_MATCH if available >= required else MatchType.PARTIAL_MATCH
    return score, match_type


def condition_score(
    material_condition: MaterialCondition,
    minimum: MaterialCondition,
    allow_lower: bool,
) -> Optional[float]:
    mat_rank = CONDITION_RANK[material_condition]
    min_rank = CONDITION_RANK[minimum]
    if mat_rank < min_rank and not allow_lower:
        return None
    if mat_rank >= min_rank:
        return 20.0
    return 10.0


def availability_by_type(av_type: AvailabilityType, custom: Optional[date]) -> date:
    today = date.today()
    if av_type == AvailabilityType.READY:
        return today
    if av_type == AvailabilityType.WITHIN_7_DAYS:
        return today + timedelta(days=7)
    if av_type == AvailabilityType.WITHIN_30_DAYS:
        return today + timedelta(days=30)
    return custom or today + timedelta(days=365)


def availability_score(mat_avail: date, required: date) -> Optional[float]:
    if mat_avail > required:
        return None
    days_early = (required - mat_avail).days
    if days_early >= 14:
        return 10.0
    if days_early >= 7:
        return 8.0
    if days_early >= 0:
        return 6.0
    return None


def location_score(
    req_lat: Optional[float],
    req_lon: Optional[float],
    req_city: str,
    mat_lat: Optional[float],
    mat_lon: Optional[float],
    mat_city: str,
    max_distance_km: Optional[float],
) -> tuple[float, Optional[float], bool]:
    if req_lat is not None and req_lon is not None and mat_lat is not None and mat_lon is not None:
        dist = haversine_km(req_lat, req_lon, mat_lat, mat_lon)
        if max_distance_km is not None and dist > max_distance_km:
            return 0.0, dist, False
        if max_distance_km:
            ratio = max(0.0, 1.0 - dist / max_distance_km)
        else:
            ratio = max(0.0, 1.0 - min(dist, 500) / 500)
        return ratio * 15.0, dist, False
    if req_city.strip().lower() == mat_city.strip().lower():
        return 10.0, None, True
    return 3.0, None, True


def compatibility_label(score: float) -> CompatibilityLabel:
    if score >= 80:
        return CompatibilityLabel.HIGHLY_SUITABLE
    if score >= 60:
        return CompatibilityLabel.MODERATELY_SUITABLE
    return CompatibilityLabel.LOW_SUITABILITY


class MatchingService:
    def match_requirement_to_materials(
        self,
        requirement: dict,
        materials: List[dict],
        sort_by: str = "matching_score",
        sort_order: str = "desc",
        min_score: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        req_cat = str(requirement.get("category_id"))
        req_unit = requirement.get("unit")
        req_qty = float(requirement.get("required_quantity", 0))
        min_cond = MaterialCondition(requirement.get("minimum_acceptable_condition"))
        allow_lower = requirement.get("allow_lower_quality", False)
        req_date = requirement.get("required_availability_date")
        if isinstance(req_date, str):
            req_date = date.fromisoformat(req_date)
        elif isinstance(req_date, datetime):
            req_date = req_date.date()

        for mat in materials:
            if mat.get("listing_status") != ListingStatus.ACTIVE.value:
                continue
            if str(mat.get("category_id")) != req_cat:
                continue
            if mat.get("unit") != req_unit:
                continue
            if str(mat.get("company_id")) == str(requirement.get("company_id")):
                continue

            type_pts = material_type_score(
                requirement.get("material_type", ""),
                mat.get("material_type", ""),
                same_category=True,
            )
            if type_pts <= 0:
                continue

            avail_qty = float(mat.get("available_quantity", 0)) - float(
                mat.get("reserved_quantity", 0)
            )
            if avail_qty <= 0:
                continue

            qty_pts, match_type = quantity_score(avail_qty, req_qty)
            cond = MaterialCondition(mat.get("material_condition"))
            cond_pts = condition_score(cond, min_cond, allow_lower)
            if cond_pts is None:
                continue

            mat_avail = availability_by_type(
                AvailabilityType(mat.get("availability_type")),
                mat.get("availability_date"),
            )
            avail_pts = availability_score(mat_avail, req_date)
            if avail_pts is None:
                continue

            loc_pts, dist_km, approx = location_score(
                requirement.get("latitude"),
                requirement.get("longitude"),
                requirement.get("preferred_location", ""),
                mat.get("latitude"),
                mat.get("longitude"),
                mat.get("location_text") or mat.get("location", ""),
                requirement.get("maximum_distance_km"),
            )
            if requirement.get("maximum_distance_km") and dist_km is not None:
                if dist_km > requirement["maximum_distance_km"]:
                    continue

            total = type_pts + qty_pts + cond_pts + loc_pts + avail_pts
            if min_score is not None and total < min_score:
                continue

            budget = requirement.get("maximum_budget")
            price = float(mat.get("expected_price", 0))
            if budget is not None and not mat.get("is_free_material") and price > budget:
                continue

            results.append(
                {
                    "material_id": str(mat["_id"]),
                    "supplier_company_id": str(mat.get("company_id")),
                    "material_title": mat.get("material_title"),
                    "available_quantity": avail_qty,
                    "required_quantity": req_qty,
                    "unit": mat.get("unit"),
                    "material_condition": mat.get("material_condition"),
                    "location": mat.get("location"),
                    "distance_km": round(dist_km, 2) if dist_km is not None else None,
                    "location_approximate": approx,
                    "availability_type": mat.get("availability_type"),
                    "expected_price": price,
                    "matching_score": round(total, 2),
                    "match_type": match_type.value,
                    "compatibility_label": compatibility_label(total).value,
                    "score_breakdown": {
                        "material_type": type_pts,
                        "quantity": round(qty_pts, 2),
                        "condition": cond_pts,
                        "location": round(loc_pts, 2),
                        "availability": avail_pts,
                    },
                }
            )

        reverse = sort_order.lower() != "asc"
        key_map = {
            "matching_score": lambda x: x["matching_score"],
            "distance_km": lambda x: x["distance_km"] if x["distance_km"] is not None else 1e9,
            "expected_price": lambda x: x["expected_price"],
            "available_quantity": lambda x: x["available_quantity"],
            "availability_type": lambda x: x["availability_type"],
        }
        key_fn = key_map.get(sort_by, key_map["matching_score"])
        results.sort(key=key_fn, reverse=reverse)
        return results

    def match_material_to_requirements(
        self,
        material: dict,
        requirements: List[dict],
        **kwargs,
    ) -> List[Dict[str, Any]]:
        pseudo_req_list = []
        for req in requirements:
            if req.get("requirement_status") != "ACTIVE":
                continue
            pseudo_req_list.append(req)
        # Reuse logic by swapping perspective: treat each req as requirement
        all_results = []
        for req in pseudo_req_list:
            matches = self.match_requirement_to_materials(req, [material], **kwargs)
            for m in matches:
                m["requirement_id"] = str(req["_id"])
                m["requirement_title"] = req.get("requirement_title")
                all_results.append(m)
        return all_results
