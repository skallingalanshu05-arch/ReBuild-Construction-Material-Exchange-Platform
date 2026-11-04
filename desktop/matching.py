"""Core matching logic for surplus C&D materials (shared with the legacy CLI)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Tuple

CONDITION_RANK = {
    "poor": 1,
    "fair": 2,
    "good": 3,
    "excellent": 4,
}

AVAILABILITY_OPTIONS = {
    "Ready": "Ready",
    "Within 7 days": "Within 7 days",
    "Within 30 days": "Within 30 days",
}

AVAILABILITY_POINTS = {
    "Ready": 10,
    "Within 7 days": 7,
    "Within 30 days": 4,
}


@dataclass
class MaterialListing:
    project: str
    material: str
    quantity: float
    condition: str
    location: str
    availability: str


@dataclass
class MaterialRequirement:
    project: str
    material: str
    quantity: float
    condition: str
    location: str


@dataclass
class MatchResult:
    score: float
    supplier: MaterialListing
    compatibility: str
    notes: List[str] = field(default_factory=list)


def normalise_condition(value: str) -> str:
    return value.strip().lower()


def calculate_match(
    supplier: MaterialListing, requirement: MaterialRequirement
) -> Optional[float]:
    if supplier.material.lower() != requirement.material.lower():
        return None

    quantity_score = min(supplier.quantity / requirement.quantity, 1) * 25

    supplier_condition = CONDITION_RANK[normalise_condition(supplier.condition)]
    required_condition = CONDITION_RANK[normalise_condition(requirement.condition)]

    if supplier_condition >= required_condition:
        condition_score = 20
    elif supplier_condition == required_condition - 1:
        condition_score = 10
    else:
        condition_score = 0

    location_score = (
        15
        if supplier.location.lower() == requirement.location.lower()
        else 5
    )

    availability_score = AVAILABILITY_POINTS.get(supplier.availability, 4)
    material_score = 30

    total = (
        material_score
        + quantity_score
        + condition_score
        + location_score
        + availability_score
    )
    return round(total, 2)


def compatibility_label(score: float) -> str:
    if score >= 80:
        return "Highly Suitable"
    if score >= 60:
        return "Moderately Suitable"
    return "Low"


def find_matches(
    listings: Iterable[MaterialListing], requirement: MaterialRequirement
) -> List[MatchResult]:
    results: List[MatchResult] = []
    req_condition = normalise_condition(requirement.condition)

    for supplier in listings:
        score = calculate_match(supplier, requirement)
        if score is None:
            continue

        notes: List[str] = []
        if supplier.quantity < requirement.quantity:
            notes.append("Available quantity is less than required.")
        if CONDITION_RANK[normalise_condition(supplier.condition)] < CONDITION_RANK[
            req_condition
        ]:
            notes.append("Material condition is below the requested level.")

        results.append(
            MatchResult(
                score=score,
                supplier=supplier,
                compatibility=compatibility_label(score),
                notes=notes,
            )
        )

    results.sort(key=lambda r: r.score, reverse=True)
    return results
