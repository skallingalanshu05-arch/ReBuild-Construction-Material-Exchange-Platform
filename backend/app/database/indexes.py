from app.database.connection import get_database


async def create_indexes() -> None:
    db = get_database()

    await db.users.create_index("email", unique=True)
    await db.users.create_index("company_id")

    await db.companies.create_index("business_email")
    await db.companies.create_index("verification_status")

    await db.projects.create_index("company_id")
    await db.projects.create_index("status")

    await db.categories.create_index("name", unique=True)
    await db.categories.create_index("is_active")

    await db.materials.create_index("company_id")
    await db.materials.create_index("category_id")
    await db.materials.create_index("listing_status")
    await db.materials.create_index([("geo", "2dsphere")], sparse=True)

    await db.requirements.create_index("company_id")
    await db.requirements.create_index("category_id")
    await db.requirements.create_index("requirement_status")
    await db.requirements.create_index([("geo", "2dsphere")], sparse=True)

    await db.requests.create_index("buyer_company_id")
    await db.requests.create_index("supplier_company_id")
    await db.requests.create_index("material_id")
    await db.requests.create_index("request_status")

    await db.transactions.create_index("buyer_company_id")
    await db.transactions.create_index("supplier_company_id")
    await db.transactions.create_index("request_id")

    await db.notifications.create_index("user_id")
    await db.notifications.create_index([("user_id", 1), ("is_read", 1)])

    await db.refresh_tokens.create_index("token_jti", unique=True)
    await db.refresh_tokens.create_index("expires_at", expireAfterSeconds=0)

    await db.password_reset_tokens.create_index("token_hash", unique=True)
    await db.password_reset_tokens.create_index("expires_at", expireAfterSeconds=0)

    await db.audit_logs.create_index("created_at")
    await db.audit_logs.create_index("user_id")
