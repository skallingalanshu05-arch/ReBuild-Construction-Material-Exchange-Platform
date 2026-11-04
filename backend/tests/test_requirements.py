import pytest
from datetime import date, timedelta
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_requirement(client: AsyncClient, auth_headers: dict):
    cat = (await client.get("/api/v1/categories")).json()["data"][0]["id"]
    res = await client.post(
        "/api/v1/requirements",
        headers=auth_headers,
        json={
            "requirement_title": "Need Bricks",
            "category_id": cat,
            "material_type": "Clay Bricks",
            "required_quantity": 500,
            "unit": "PIECE",
            "minimum_acceptable_condition": "FAIR",
            "preferred_location": "Mumbai",
            "required_availability_date": (date.today() + timedelta(days=14)).isoformat(),
            "requirement_status": "ACTIVE",
        },
    )
    assert res.status_code == 201

    mine = await client.get("/api/v1/requirements/my-requirements", headers=auth_headers)
    assert mine.status_code == 200
    assert mine.json()["data"]["total"] >= 1

    bad = await client.post(
        "/api/v1/requirements",
        headers=auth_headers,
        json={
            "requirement_title": "Bad",
            "category_id": cat,
            "material_type": "Clay Bricks",
            "required_quantity": -1,
            "unit": "PIECE",
            "minimum_acceptable_condition": "FAIR",
            "preferred_location": "Mumbai",
            "required_availability_date": date.today().isoformat(),
        },
    )
    assert bad.status_code == 422
