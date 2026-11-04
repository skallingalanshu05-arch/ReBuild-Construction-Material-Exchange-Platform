import hashlib
from datetime import timedelta
from typing import Any, Dict, Optional

from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from app.core.config import get_settings
from app.core.exceptions import AppException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_secure_token,
    hash_password,
    verify_password,
)
from app.models.user import AccountStatus, UserRole
from app.schemas.common import doc_timestamps, utc_now
from app.services.audit_service import log_audit
from app.utils.object_id import oid_to_str, str_to_object_id


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class AuthService:
    def __init__(self, db):
        self.db = db

    async def register(self, data: Dict[str, Any]) -> dict:
        if data.get("role") == UserRole.ADMIN.value:
            raise AppException("Cannot register as administrator")

        user_doc = {
            "full_name": data["full_name"],
            "email": data["email"].lower(),
            "mobile_number": data["mobile_number"],
            "password_hash": hash_password(data["password"]),
            "company_id": None,
            "role": UserRole.USER.value,
            "account_status": AccountStatus.ACTIVE.value,
            "is_active": True,
            **doc_timestamps(),
        }
        try:
            result = await self.db.users.insert_one(user_doc)
        except DuplicateKeyError as exc:
            raise AppException("Email already registered", status_code=409) from exc

        user_id = str(result.inserted_id)
        await log_audit(self.db, "user.register", user_id=user_id)
        return await self._issue_tokens(user_id)

    async def login(self, email: str, password: str) -> dict:
        user = await self.db.users.find_one({"email": email.lower()})
        if not user or not verify_password(password, user["password_hash"]):
            raise AppException("Invalid email or password", status_code=401)
        if not user.get("is_active", True):
            raise AppException("Account is deactivated", status_code=403)
        return await self._issue_tokens(str(user["_id"]))

    async def _issue_tokens(self, user_id: str) -> dict:
        user = await self.db.users.find_one({"_id": str_to_object_id(user_id)})
        access = create_access_token(
            user_id,
            extra={"role": user.get("role"), "company_id": user.get("company_id")},
        )
        refresh = create_refresh_token(user_id)
        payload = decode_token(refresh)
        settings = get_settings()
        await self.db.refresh_tokens.insert_one(
            {
                "user_id": user_id,
                "token_jti": payload["jti"],
                "revoked": False,
                "expires_at": utc_now() + timedelta(days=settings.jwt_refresh_token_expire_days),
                "created_at": utc_now(),
            }
        )
        return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}

    async def refresh(self, refresh_token: str) -> dict:
        try:
            payload = decode_token(refresh_token)
        except Exception as exc:
            raise AppException("Invalid refresh token", status_code=401) from exc
        if payload.get("type") != "refresh":
            raise AppException("Invalid refresh token", status_code=401)
        jti = payload.get("jti")
        stored = await self.db.refresh_tokens.find_one({"token_jti": jti, "revoked": False})
        if not stored:
            raise AppException("Refresh token revoked or not found", status_code=401)
        user_id = payload.get("sub")
        return await self._issue_tokens(user_id)

    async def logout(self, refresh_token: Optional[str], user_id: str) -> None:
        if refresh_token:
            try:
                payload = decode_token(refresh_token)
                jti = payload.get("jti")
                if jti:
                    await self.db.refresh_tokens.update_one(
                        {"token_jti": jti}, {"$set": {"revoked": True}}
                    )
            except Exception:
                pass
        await log_audit(self.db, "user.logout", user_id=user_id)

    async def get_me(self, user_id: str) -> dict:
        user = await self.db.users.find_one({"_id": str_to_object_id(user_id)})
        if not user:
            raise AppException("User not found", status_code=404)
        return self._public_user(user)

    async def update_profile(self, user_id: str, updates: dict) -> dict:
        allowed = {k: v for k, v in updates.items() if v is not None and k in ("full_name", "mobile_number")}
        if not allowed:
            raise AppException("No valid fields to update")
        allowed["updated_at"] = utc_now()
        await self.db.users.update_one({"_id": str_to_object_id(user_id)}, {"$set": allowed})
        return await self.get_me(user_id)

    async def change_password(self, user_id: str, current: str, new_password: str) -> None:
        user = await self.db.users.find_one({"_id": str_to_object_id(user_id)})
        if not user or not verify_password(current, user["password_hash"]):
            raise AppException("Current password is incorrect", status_code=400)
        await self.db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"password_hash": hash_password(new_password), "updated_at": utc_now()}},
        )
        await self.db.refresh_tokens.update_many(
            {"user_id": user_id}, {"$set": {"revoked": True}}
        )
        await log_audit(self.db, "user.change_password", user_id=user_id)

    async def forgot_password(self, email: str) -> None:
        user = await self.db.users.find_one({"email": email.lower()})
        if not user:
            return
        token = generate_secure_token()
        settings = get_settings()
        await self.db.password_reset_tokens.insert_one(
            {
                "user_id": str(user["_id"]),
                "token_hash": _hash_token(token),
                "used": False,
                "expires_at": utc_now()
                + timedelta(hours=settings.password_reset_token_expire_hours),
                "created_at": utc_now(),
            }
        )
        await log_audit(self.db, "user.forgot_password", user_id=str(user["_id"]))
        # Email delivery integration point: send `token` to the user's inbox.
        if get_settings().debug:
            await log_audit(
                self.db,
                "user.forgot_password.dev_token",
                user_id=str(user["_id"]),
                details={"hint": "Configure email provider in production"},
            )

    async def reset_password(self, token: str, new_password: str) -> None:
        token_hash = _hash_token(token)
        record = await self.db.password_reset_tokens.find_one(
            {"token_hash": token_hash, "used": False}
        )
        if not record or record.get("expires_at") < utc_now():
            raise AppException("Invalid or expired reset token", status_code=400)
        await self.db.users.update_one(
            {"_id": str_to_object_id(record["user_id"])},
            {"$set": {"password_hash": hash_password(new_password), "updated_at": utc_now()}},
        )
        await self.db.password_reset_tokens.update_one(
            {"_id": record["_id"]}, {"$set": {"used": True}}
        )
        await self.db.refresh_tokens.update_many(
            {"user_id": record["user_id"]}, {"$set": {"revoked": True}}
        )

    async def set_user_active(self, user_id: str, is_active: bool) -> dict:
        status = AccountStatus.ACTIVE.value if is_active else AccountStatus.INACTIVE.value
        await self.db.users.update_one(
            {"_id": str_to_object_id(user_id)},
            {"$set": {"is_active": is_active, "account_status": status, "updated_at": utc_now()}},
        )
        return await self.get_me(user_id)

    def _public_user(self, user: dict) -> dict:
        data = oid_to_str(user)
        data.pop("password_hash", None)
        return data
