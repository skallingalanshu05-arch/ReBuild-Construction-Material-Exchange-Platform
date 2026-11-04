from app.database.connection import get_database
from app.services.auth_service import AuthService
from app.services.material_service import MaterialService
from app.services.matching_service import MatchingService
from app.services.notification_service import NotificationService
from app.services.request_service import RequestService


def get_auth_service() -> AuthService:
    return AuthService(get_database())


def get_material_service() -> MaterialService:
    return MaterialService(get_database())


def get_matching_service() -> MatchingService:
    return MatchingService()


def get_request_service() -> RequestService:
    return RequestService(get_database())


def get_notification_service() -> NotificationService:
    return NotificationService(get_database())
