from fastapi import APIRouter, Depends, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.api.deps import get_auth_service
from app.core.permissions import get_current_user
from app.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
)
from app.schemas.user import UserUpdate
from app.services.auth_service import AuthService
from app.utils.response import success_data, success_response

router = APIRouter(prefix="/auth", tags=["Authentication"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(request: Request, body: RegisterRequest, auth: AuthService = Depends(get_auth_service)):
    tokens = await auth.register(body.model_dump())
    return success_response(tokens, "Registration successful", status.HTTP_201_CREATED)


@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, body: LoginRequest, auth: AuthService = Depends(get_auth_service)):
    tokens = await auth.login(body.email, body.password)
    return success_data(tokens, "Login successful")


@router.post("/refresh")
async def refresh(body: RefreshRequest, auth: AuthService = Depends(get_auth_service)):
    tokens = await auth.refresh(body.refresh_token)
    return success_data(tokens, "Token refreshed")


@router.post("/logout")
async def logout(
    body: LogoutRequest,
    user=Depends(get_current_user),
    auth: AuthService = Depends(get_auth_service),
):
    await auth.logout(body.refresh_token, user["id"])
    return success_data(None, "Logged out")


@router.get("/me")
async def me(user=Depends(get_current_user), auth: AuthService = Depends(get_auth_service)):
    data = await auth.get_me(user["id"])
    return success_data(data)


@router.patch("/me")
async def update_me(
    body: UserUpdate,
    user=Depends(get_current_user),
    auth: AuthService = Depends(get_auth_service),
):
    data = await auth.update_profile(user["id"], body.model_dump(exclude_unset=True))
    return success_data(data, "Profile updated")


@router.post("/change-password")
async def change_password(
    body: ChangePasswordRequest,
    user=Depends(get_current_user),
    auth: AuthService = Depends(get_auth_service),
):
    await auth.change_password(user["id"], body.current_password, body.new_password)
    return success_data(None, "Password changed")


@router.post("/forgot-password")
@limiter.limit("5/minute")
async def forgot_password(
    request: Request,
    body: ForgotPasswordRequest,
    auth: AuthService = Depends(get_auth_service),
):
    await auth.forgot_password(body.email)
    return success_data(None, "If the email exists, a reset link has been sent")


@router.post("/reset-password")
async def reset_password(body: ResetPasswordRequest, auth: AuthService = Depends(get_auth_service)):
    await auth.reset_password(body.token, body.new_password)
    return success_data(None, "Password reset successful")
