import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_and_login(client: AsyncClient):
    res = await client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Alice",
            "email": "alice@test.com",
            "mobile_number": "9000000001",
            "password": "SecurePass1",
        },
    )
    assert res.status_code == 201
    assert res.json()["success"] is True
    assert "access_token" in res.json()["data"]

    dup = await client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Alice2",
            "email": "alice@test.com",
            "mobile_number": "9000000002",
            "password": "SecurePass1",
        },
    )
    assert dup.status_code == 409

    bad = await client.post(
        "/api/v1/auth/login",
        json={"email": "alice@test.com", "password": "WrongPass1"},
    )
    assert bad.status_code == 401

    ok = await client.post(
        "/api/v1/auth/login",
        json={"email": "alice@test.com", "password": "SecurePass1"},
    )
    assert ok.status_code == 200
    token = ok.json()["data"]["access_token"]

    me = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["data"]["email"] == "alice@test.com"


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    res = await client.get("/api/v1/auth/me")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_expired_token_invalid(client: AsyncClient):
    res = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    assert res.status_code == 401
