from typing import Any, Optional

from app.schemas.common import utc_now


async def log_audit(
    db,
    action: str,
    user_id: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[dict] = None,
) -> None:
    await db.audit_logs.insert_one(
        {
            "action": action,
            "user_id": user_id,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details or {},
            "created_at": utc_now(),
        }
    )
