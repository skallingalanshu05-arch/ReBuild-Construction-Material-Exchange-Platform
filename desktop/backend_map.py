"""Map desktop forms to FastAPI / Mongo payloads."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from material_types import MaterialTypeSpec, get_spec

UI_CONDITION_TO_API = {
    "poor": "POOR",
    "fair": "FAIR",
    "good": "GOOD",
    "excellent": "EXCELLENT",
}

DESKTOP_UNIT_TO_API = {
    "nos": "PIECE",
    "ton": "TONNE",
    "kg": "KG",
    "m3": "CUBIC_METER",
}

API_UNIT_TO_DESKTOP = {v: k for k, v in DESKTOP_UNIT_TO_API.items()}

AVAILABILITY_TO_API = {
    "Ready": "READY",
    "Within 7 days": "WITHIN_7_DAYS",
    "Within 30 days": "WITHIN_30_DAYS",
}

API_AVAILABILITY_TO_DESKTOP = {v: k for k, v in AVAILABILITY_TO_API.items()}


def to_api_condition(value: str) -> str:
    return UI_CONDITION_TO_API.get(value.strip().lower(), value.upper())


def to_api_unit(unit: str) -> str:
    return DESKTOP_UNIT_TO_API.get(unit.strip().lower(), "OTHER")


def from_api_unit(unit: Optional[str]) -> str:
    if not unit:
        return "nos"
    return API_UNIT_TO_DESKTOP.get(unit.upper(), unit.lower())


def from_api_condition(value: Optional[str]) -> str:
    if not value:
        return "good"
    return value.strip().lower()


def from_api_availability(value: Optional[str]) -> str:
    if not value:
        return "Ready"
    return API_AVAILABILITY_TO_DESKTOP.get(value.upper(), value)


def as_list(data: Any) -> List[Dict[str, Any]]:
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("items", "data", "results"):
            val = data.get(key)
            if isinstance(val, list):
                return val
    return []


def category_id_for_material(
    categories: List[Dict[str, Any]], spec: MaterialTypeSpec
) -> Optional[str]:
    target = spec.category_name.lower()
    for cat in categories:
        name = str(cat.get("name", "")).lower()
        if name == target:
            return str(cat.get("id") or cat.get("_id"))
    return None


def build_material_create_payload(
    *,
    spec: MaterialTypeSpec,
    category_id: str,
    project_name: str,
    quantity: float,
    unit: str,
    condition: str,
    location: str,
    availability: str,
) -> Dict[str, Any]:
    title = f"{spec.key} — {project_name}".strip(" —")
    return {
        "material_title": title[:200],
        "material_description": f"Project: {project_name}. Listed via ReBuild desktop.",
        "category_id": category_id,
        "material_type": spec.key,
        "available_quantity": quantity,
        "unit": to_api_unit(unit),
        "material_condition": to_api_condition(condition),
        "expected_price": 0,
        "location": location,
        "availability_type": AVAILABILITY_TO_API.get(availability, "READY"),
        "listing_status": "ACTIVE",
    }


def doc_to_listing(doc: Dict[str, Any]) -> "MaterialListing":
    from matching import MaterialListing

    material = str(doc.get("material_type") or doc.get("material_title") or "Material")
    return MaterialListing(
        project=str(doc.get("material_title") or "Supplier listing")[:80],
        material=material,
        quantity=float(doc.get("available_quantity") or 0),
        unit=from_api_unit(doc.get("unit")),
        condition=from_api_condition(doc.get("material_condition")),
        location=str(doc.get("location") or doc.get("location_text") or ""),
        availability=from_api_availability(doc.get("availability_type")),
    )


def listing_matches_type(doc: Dict[str, Any], material_key: str) -> bool:
    mt = str(doc.get("material_type") or "").lower()
    title = str(doc.get("material_title") or "").lower()
    key = material_key.lower()
    return mt == key or key in title
