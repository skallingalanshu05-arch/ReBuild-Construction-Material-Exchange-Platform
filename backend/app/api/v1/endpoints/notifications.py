from fastapi import APIRouter, Depends, Query

from app.api.deps import get_notification_service
from app.core.permissions import get_current_user
from app.services.notification_service import NotificationService
from app.utils.response import success_data

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("")
async def list_notifications(
    user=Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: NotificationService = Depends(get_notification_service),
):
    data = await service.list_for_user(user["id"], page=page, page_size=page_size)
    return success_data(data)


@router.patch("/{notification_id}/read")
async def mark_read(
    notification_id: str,
    user=Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    data = await service.mark_read(notification_id, user["id"])
    return success_data(data, "Notification marked as read")


@router.patch("/read-all")
async def mark_all_read(
    user=Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    count = await service.mark_all_read(user["id"])
    return success_data({"updated": count}, "All notifications marked as read")


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    user=Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    await service.delete(notification_id, user["id"])
    return success_data(None, "Notification deleted")
