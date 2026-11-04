"""Fixed material catalogue and units for the desktop app."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

UNIT_LABELS = {
    "nos": "nos (pieces)",
    "ton": "ton",
    "kg": "kg",
    "m3": "m³ (cubic metre)",
}


@dataclass(frozen=True)
class MaterialTypeSpec:
    key: str
    category_name: str
    units: tuple[str, ...]
    default_unit: str
    quantity_hint: str

    @property
    def allows_unit_choice(self) -> bool:
        return len(self.units) > 1


MATERIAL_TYPES: Dict[str, MaterialTypeSpec] = {
    "Window frame": MaterialTypeSpec(
        key="Window frame",
        category_name="Doors and Windows",
        units=("nos",),
        default_unit="nos",
        quantity_hint="Enter number of window frames (nos / pieces).",
    ),
    "Door frame": MaterialTypeSpec(
        key="Door frame",
        category_name="Doors and Windows",
        units=("nos",),
        default_unit="nos",
        quantity_hint="Enter number of door frames (nos / pieces).",
    ),
    "Steel": MaterialTypeSpec(
        key="Steel",
        category_name="Steel and Metal",
        units=("ton", "kg"),
        default_unit="ton",
        quantity_hint="Enter steel quantity — choose ton or kg below.",
    ),
    "Brick": MaterialTypeSpec(
        key="Brick",
        category_name="Bricks and Blocks",
        units=("nos",),
        default_unit="nos",
        quantity_hint="Enter number of bricks (nos / pieces).",
    ),
    "Aggregate": MaterialTypeSpec(
        key="Aggregate",
        category_name="Aggregates",
        units=("m3",),
        default_unit="m3",
        quantity_hint="Enter volume in cubic metres (m³).",
    ),
}

MATERIAL_TYPE_NAMES: List[str] = list(MATERIAL_TYPES.keys())


def get_spec(material_name: str) -> Optional[MaterialTypeSpec]:
    if not material_name:
        return None
    direct = MATERIAL_TYPES.get(material_name)
    if direct:
        return direct
    lower = material_name.strip().lower()
    for spec in MATERIAL_TYPES.values():
        if spec.key.lower() == lower:
            return spec
    return None


def format_unit(unit: str) -> str:
    return UNIT_LABELS.get(unit, unit)


def quantity_field_label(material_name: str, unit: str) -> str:
    spec = get_spec(material_name)
    name = spec.key if spec else material_name or "Material"
    return f"Quantity — {name} ({format_unit(unit)})"


def resolve_unit(material_name: str, selected_unit: str) -> str:
    spec = get_spec(material_name)
    if not spec:
        return selected_unit or "nos"
    if selected_unit in spec.units:
        return selected_unit
    return spec.default_unit
