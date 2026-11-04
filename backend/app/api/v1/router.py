from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    auth,
    categories,
    companies,
    matches,
    materials,
    notifications,
    projects,
    requirements,
    requests,
    transactions,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(companies.router)
api_router.include_router(projects.router)
api_router.include_router(categories.router)
api_router.include_router(materials.router)
api_router.include_router(requirements.router)
api_router.include_router(matches.router)
api_router.include_router(requests.router)
api_router.include_router(transactions.router)
api_router.include_router(notifications.router)
api_router.include_router(admin.router)
