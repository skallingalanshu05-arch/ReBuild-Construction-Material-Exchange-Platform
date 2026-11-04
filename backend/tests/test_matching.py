from datetime import date, timedelta

import pytest

from app.models.material import AvailabilityType, MaterialCondition, MeasurementUnit
from app.services.matching_service import MatchingService


def _material(**overrides):
    base = {
        "_id": "507f1f77bcf86cd799439011",
        "category_id": "cat1",
        "material_type": "Clay Bricks",
        "company_id": "sup1",
        "material_title": "Bricks",
        "available_quantity": 1000,
        "reserved_quantity": 0,
        "unit": MeasurementUnit.PIECE.value,
        "material_condition": MaterialCondition.GOOD.value,
        "listing_status": "ACTIVE",
        "location_text": "Mumbai",
        "latitude": 19.076,
        "longitude": 72.8777,
        "availability_type": AvailabilityType.READY.value,
        "expected_price": 4,
        "is_free_material": False,
    }
    base.update(overrides)
    return base


def _requirement(**overrides):
    base = {
        "company_id": "buy1",
        "category_id": "cat1",
        "material_type": "Clay Bricks",
        "required_quantity": 500,
        "unit": MeasurementUnit.PIECE.value,
        "minimum_acceptable_condition": MaterialCondition.FAIR.value,
        "allow_lower_quality": False,
        "preferred_location": "Mumbai",
        "latitude": 19.08,
        "longitude": 72.88,
        "required_availability_date": date.today() + timedelta(days=10),
    }
    base.update(overrides)
    return base


@pytest.mark.asyncio
async def test_exact_match_full_quantity():
    svc = MatchingService()
    results = svc.match_requirement_to_materials(_requirement(), [_material()])
    assert len(results) == 1
    r = results[0]
    assert r["match_type"] == "FULL_MATCH"
    assert r["matching_score"] >= 80
    assert r["score_breakdown"]["material_type"] == 30


@pytest.mark.asyncio
async def test_partial_quantity():
    svc = MatchingService()
    results = svc.match_requirement_to_materials(
        _requirement(required_quantity=2000), [_material(available_quantity=500)]
    )
    assert results[0]["match_type"] == "PARTIAL_MATCH"
    assert results[0]["score_breakdown"]["quantity"] == pytest.approx(6.25, rel=0.01)


@pytest.mark.asyncio
async def test_different_material_type_excluded():
    svc = MatchingService()
    results = svc.match_requirement_to_materials(
        _requirement(material_type="Portland Cement"),
        [_material(material_type="Clay Bricks", category_id="cat2")],
    )
    assert len(results) == 0


@pytest.mark.asyncio
async def test_insufficient_quality_excluded():
    svc = MatchingService()
    results = svc.match_requirement_to_materials(
        _requirement(minimum_acceptable_condition=MaterialCondition.EXCELLENT.value),
        [_material(material_condition=MaterialCondition.POOR.value)],
    )
    assert len(results) == 0


@pytest.mark.asyncio
async def test_availability_mismatch_excluded():
    svc = MatchingService()
    results = svc.match_requirement_to_materials(
        _requirement(required_availability_date=date.today()),
        [
            _material(
                availability_type=AvailabilityType.CUSTOM_DATE.value,
                availability_date=date.today() + timedelta(days=30),
            )
        ],
    )
    assert len(results) == 0
