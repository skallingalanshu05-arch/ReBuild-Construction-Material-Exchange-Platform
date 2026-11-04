import os
import sys
import uuid
from pathlib import Path
from typing import AsyncGenerator

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# Use isolated test database before app imports settings-backed connection
os.environ.setdefault("MONGODB_DATABASE", "rebuild_test_db")
os.environ.setdefault("JWT_SECRET_KEY", "test_secret_key_for_pytest_only")
os.environ.setdefault("MONGODB_SUPPORTS_TRANSACTIONS", "false")
os.environ.setdefault("TESTING", "true")

from app.database.connection import close_mongo_connection, connect_to_mongo, get_database
from app.main import app


@pytest_asyncio.fixture(scope="session")
async def _mongo_session():
    await connect_to_mongo()
    from app.database.indexes import create_indexes
    from app.database.seed import seed_categories

    db = get_database()
    await create_indexes()
    await seed_categories(db)
    yield
    await close_mongo_connection()


@pytest_asyncio.fixture(autouse=True)
async def clean_db(_mongo_session):
    db = get_database()
    for name in await db.list_collection_names():
        await db.drop_collection(name)
    from app.database.indexes import create_indexes
    from app.database.seed import seed_categories

    await create_indexes()
    await seed_categories(db)


@pytest_asyncio.fixture
async def client(_mongo_session) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient):
    email = f"buyer_{uuid.uuid4().hex[:8]}@example.com"
    password = "SecurePass1"
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Test Buyer",
            "email": email,
            "mobile_number": "9876543210",
            "password": password,
        },
    )
    assert reg.status_code == 201
    token = reg.json()["data"]["access_token"]
    await client.post(
        "/api/v1/companies",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "company_name": "Buyer Co",
            "business_email": "biz@buyer.com",
            "phone_number": "9876543210",
            "address": "1 Main St",
            "city": "Mumbai",
            "state": "MH",
            "country": "IN",
            "postal_code": "400001",
            "is_supplier": True,
            "is_buyer": True,
        },
    )
    login = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = login.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def supplier_headers(client: AsyncClient):
    email = f"supplier_{uuid.uuid4().hex[:8]}@example.com"
    password = "SecurePass1"
    await client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Test Supplier",
            "email": email,
            "mobile_number": "9876543211",
            "password": password,
        },
    )
    login = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = login.json()["data"]["access_token"]
    await client.post(
        "/api/v1/companies",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "company_name": "Supplier Co",
            "business_email": "biz@supplier.com",
            "phone_number": "9876543211",
            "address": "2 Market Rd",
            "city": "Mumbai",
            "state": "MH",
            "country": "IN",
            "postal_code": "400002",
            "is_supplier": True,
            "is_buyer": False,
        },
    )
    login = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = login.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}
