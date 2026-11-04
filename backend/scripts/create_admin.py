#!/usr/bin/env python3
"""Create the first platform administrator (CLI only — not exposed via API)."""

import asyncio
import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pymongo import AsyncMongoClient

from app.core.config import get_settings
from app.core.security import hash_password
from app.models.user import AccountStatus, UserRole
from app.schemas.common import doc_timestamps


async def main() -> None:
    settings = get_settings()
    email = input("Admin email: ").strip().lower()
    full_name = input("Full name: ").strip()
    mobile = input("Mobile number: ").strip()
    password = getpass.getpass("Password: ")
    password2 = getpass.getpass("Confirm password: ")
    if password != password2:
        print("Passwords do not match")
        sys.exit(1)

    client = AsyncMongoClient(settings.mongodb_url)
    db = client[settings.mongodb_database]
    existing = await db.users.find_one({"email": email})
    if existing:
        print("User with this email already exists")
        sys.exit(1)

    doc = {
        "full_name": full_name,
        "email": email,
        "mobile_number": mobile,
        "password_hash": hash_password(password),
        "company_id": None,
        "role": UserRole.ADMIN.value,
        "account_status": AccountStatus.ACTIVE.value,
        "is_active": True,
        **doc_timestamps(),
    }
    result = await db.users.insert_one(doc)
    print(f"Administrator created with id: {result.inserted_id}")
    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
