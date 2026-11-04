from datetime import date, timedelta

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_request_flow(client: AsyncClient, auth_headers: dict, supplier_headers: dict):
    cat = (await client.get("/api/v1/categories")).json()["data"][0]["id"]

    mat = await client.post(
        "/api/v1/materials",
        headers=supplier_headers,
        json={
            "material_title": "Brick Stock",
            "category_id": cat,
            "material_type": "Clay Bricks",
            "available_quantity": 100,
            "unit": "PIECE",
            "material_condition": "GOOD",
            "expected_price": 3,
            "location": "Mumbai",
            "availability_type": "READY",
            "listing_status": "ACTIVE",
        },
    )
    material_id = mat.json()["data"]["id"]

    req = await client.post(
        "/api/v1/requests",
        headers=auth_headers,
        json={"material_id": material_id, "requested_quantity": 10, "offered_price": 3},
    )
    assert req.status_code == 200
    request_id = req.json()["data"]["id"]

    accept = await client.patch(
        f"/api/v1/requests/{request_id}/accept",
        headers=supplier_headers,
    )
    assert accept.status_code == 200

    confirm = await client.patch(
        f"/api/v1/requests/{request_id}/confirm",
        headers=auth_headers,
    )
    assert confirm.status_code == 200

    oversell = await client.post(
        "/api/v1/requests",
        headers=auth_headers,
        json={"material_id": material_id, "requested_quantity": 500, "offered_price": 3},
    )
    assert oversell.status_code == 400

    unauthorized = await client.patch(
        f"/api/v1/requests/{request_id}/accept",
        headers=auth_headers,
    )
    assert unauthorized.status_code == 403
