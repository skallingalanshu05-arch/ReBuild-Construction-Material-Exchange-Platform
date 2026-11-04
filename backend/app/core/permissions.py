from enum import Enum
from typing import Annotated, Optional

from bson import ObjectId
from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import AppException
from app.core.security import decode_token
from app.database.connection import get_database
from app.models.user import UserRole
from app.utils.object_id import str_to_object_id

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security_scheme)],
):
    if not credentials or not credentials.credentials:
        raise AppException("Not authenticated", status_code=status.HTTP_401_UNAUTHORIZED)
    try:
        payload = decode_token(credentials.credentials)
    except Exception as exc:
        raise AppException("Invalid or expired token", status_code=status.HTTP_401_UNAUTHORIZED) from exc
    if payload.get("type") != "access":
        raise AppException("Invalid token type", status_code=status.HTTP_401_UNAUTHORIZED)
    user_id = payload.get("sub")
    if not user_id:
        raise AppException("Invalid token payload", status_code=status.HTTP_401_UNAUTHORIZED)

    db = get_database()
    user = await db.users.find_one({"_id": str_to_object_id(user_id)})
    if not user:
        raise AppException("User not found", status_code=status.HTTP_401_UNAUTHORIZED)
    if not user.get("is_active", True):
        raise AppException("Account is deactivated", status_code=status.HTTP_403_FORBIDDEN)
    user["id"] = str(user["_id"])
    return user


async def get_current_active_user(user=Depends(get_current_user)):
    return user


async def require_admin(user=Depends(get_current_user)):
    if user.get("role") != UserRole.ADMIN.value:
        raise AppException("Administrator access required", status_code=status.HTTP_403_FORBIDDEN)
    return user


def user_company_id(user: dict) -> Optional[ObjectId]:
    cid = user.get("company_id")
    if not cid:
        return None
    return str_to_object_id(cid) if isinstance(cid, str) else cid


async def ensure_company_member(user: dict, company_id: str) -> None:
    if user.get("role") == UserRole.ADMIN.value:
        return
    if str(user.get("company_id")) != str(company_id):
        raise AppException("Not authorized for this company", status_code=status.HTTP_403_FORBIDDEN)
