from typing import Any, Dict, List, Optional

from app.models.notification import NotificationType
from app.schemas.common import utc_now
from app.utils.object_id import oid_to_str, str_to_object_id


class NotificationService:
    def __init__(self, db):
        self.db = db

    async def create(
        self,
        user_id: str,
        notification_type: NotificationType,
        title: str,
        body: str,
        metadata: Optional[dict] = None,
    ) -> dict:
        doc = {
            "user_id": user_id,
            "notification_type": notification_type.value,
            "title": title,
            "body": body,
            "metadata": metadata or {},
            "is_read": False,
            "created_at": utc_now(),
        }
        result = await self.db.notifications.insert_one(doc)
        doc["_id"] = result.inserted_id
        return oid_to_str(doc)

    async def list_for_user(self, user_id: str, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        from app.utils.pagination import paginated_meta, pagination_params

        pg = pagination_params(page, page_size)
        query = {"user_id": user_id}
        total = await self.db.notifications.count_documents(query)
        cursor = (
            self.db.notifications.find(query)
            .sort("created_at", -1)
            .skip(pg["skip"])
            .limit(pg["limit"])
        )
        items = [oid_to_str(n) async for n in cursor]
        unread = await self.db.notifications.count_documents({"user_id": user_id, "is_read": False})
        return {
            "items": items,
            "unread_count": unread,
            **paginated_meta(total, pg["page"], pg["page_size"]),
        }

    async def mark_read(self, notification_id: str, user_id: str) -> dict:
        doc = await self.db.notifications.find_one(
            {"_id": str_to_object_id(notification_id), "user_id": user_id}
        )
        if not doc:
            from app.core.exceptions import AppException

            raise AppException("Notification not found", status_code=404)
        await self.db.notifications.update_one(
            {"_id": doc["_id"]}, {"$set": {"is_read": True}}
        )
        doc["is_read"] = True
        return oid_to_str(doc)

    async def mark_all_read(self, user_id: str) -> int:
        result = await self.db.notifications.update_many(
            {"user_id": user_id, "is_read": False}, {"$set": {"is_read": True}}
        )
        return result.modified_count

    async def delete(self, notification_id: str, user_id: str) -> None:
        result = await self.db.notifications.delete_one(
            {"_id": str_to_object_id(notification_id), "user_id": user_id}
        )
        if result.deleted_count == 0:
            from app.core.exceptions import AppException

            raise AppException("Notification not found", status_code=404)
