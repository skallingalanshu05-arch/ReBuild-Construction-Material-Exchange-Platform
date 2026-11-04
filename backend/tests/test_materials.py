import pytest
from httpx import AsyncClient


async def _category_id(client: AsyncClient) -> str:
    res = await client.get("/api/v1/categories")
    return res.json()["data"][0]["id"]


@pytest.mark.asyncio
async def test_create_and_update_material(client: AsyncClient, supplier_headers: dict):
    cat = await _category_id(client)
    create = await client.post(
        "/api/v1/materials",
        headers=supplier_headers,
        json={
            "material_title": "Surplus Bricks",
            "category_id": cat,
            "material_type": "Clay Bricks",
            "available_quantity": 1000,
            "unit": "PIECE",
            "material_condition": "GOOD",
            "expected_price": 5,
            "location": "Mumbai",
            "latitude": 19.076,
            "longitude": 72.8777,
            "availability_type": "READY",
            "listing_status": "ACTIVE",
        },
    )
    assert create.status_code == 201
    material_id = create.json()["data"]["id"]

    bad = await client.post(
        "/api/v1/materials",
        headers=supplier_headers,
        json={
            "material_title": "Bad Qty",
            "category_id": cat,
            "material_type": "Clay Bricks",
            "available_quantity": 0,
            "unit": "PIECE",
            "material_condition": "GOOD",
            "location": "Mumbai",
            "availability_type": "READY",
        },
    )
    assert bad.status_code == 422

    other = await client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Intruder",
            "email": "intruder@test.com",
            "mobile_number": "9000000099",
            "password": "SecurePass1",
        },
    )
    token = other.json()["data"]["access_token"]
    patch = await client.patch(
        f"/api/v1/materials/{material_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"material_title": "Hacked"},
    )
    assert patch.status_code in (400, 403)

    upd = await client.patch(
        f"/api/v1/materials/{material_id}",
        headers=supplier_headers,
        json={"available_quantity": 900},
    )
    assert upd.status_code == 200

    await client.delete(f"/api/v1/materials/{material_id}", headers=supplier_headers)
