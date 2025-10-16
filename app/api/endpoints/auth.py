from fastapi import APIRouter, Depends, status, Response, Request

# --- Dependency Imports ---
from app.service.auth import AuthService
from app.di.core import get_auth_service, get_current_user
from app.model.user import User

# --- Pydantic Schema Imports ---
from app.schema.auth.request import UserLoginRequest, UserCreateRequest
from app.schema.auth.response import SingleUserResponse
from app.schema.base_response import BaseSingleResponse

# --- Router Initialization ---
router = APIRouter(prefix="/auth", tags=["Authentication"])
from app.di.deps import get_current_user

# --- API Endpoints ---

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=SingleUserResponse)
async def register_user(
    request_data: UserCreateRequest,
    service: AuthService = Depends(get_auth_service),
    current_user: User = Depends(get_current_user),
):
    """### Register a new User."""
    return await service.register(user_create=request_data)

@router.post("/login", response_model=BaseSingleResponse)
async def login_for_cookie(
    response: Response,
    request_data: UserLoginRequest,
    service: AuthService = Depends(get_auth_service),
):
    """### Login user and set access/refresh cookies."""
    return await service.login(form_data=request_data, response=response)

@router.post("/logout", response_model=BaseSingleResponse)
async def logout(
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service),
):
    """### Logout user and clear cookies."""
    return await service.logout(request=request, response=response)

@router.post("/refresh", response_model=BaseSingleResponse)
async def refresh_access_token(
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service),
):
    """### Refresh access token using the refresh cookie."""
    return await service.refresh(request=request, response=response)

@router.get("/me", response_model=SingleUserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
):
    """### Get current authenticated user's profile."""
    return await service.get_me(current_user=current_user)