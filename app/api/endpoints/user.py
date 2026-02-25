import uuid
from fastapi import APIRouter, Depends, status, Query

from app.service.user import UserService
from app.di.core import get_user_service
from app.di.deps import require_admin_or_root, get_current_user
from app.model.user import User
from app.schema.user.request import UserCreateByAdminRequest, UserUpdateRequest
from app.schema.user.response import UserListResponse, SingleUserFullResponse
from app.schema.base_response import BaseSingleResponse

router = APIRouter(prefix="/users", tags=["User Management"])


@router.get("", response_model=UserListResponse)
async def list_users(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, le=500),
    _: User = Depends(require_admin_or_root),
    service: UserService = Depends(get_user_service),
):
    """### [Admin/Root] Ambil daftar semua user."""
    users = await service.list_users(skip=skip, limit=limit)
    return UserListResponse(data=users)


@router.get("/{user_id}", response_model=SingleUserFullResponse)
async def get_user(
    user_id: uuid.UUID,
    _: User = Depends(require_admin_or_root),
    service: UserService = Depends(get_user_service),
):
    """### [Admin/Root] Ambil detail satu user."""
    user = await service.get_user(user_id=user_id)
    return SingleUserFullResponse(data=user)


@router.post("", response_model=SingleUserFullResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request_data: UserCreateByAdminRequest,
    _: User = Depends(require_admin_or_root),
    service: UserService = Depends(get_user_service),
):
    """### [Admin/Root] Buat user baru dengan role yang ditentukan."""
    new_user = await service.create_user(data=request_data)
    return SingleUserFullResponse(message="User berhasil dibuat.", data=new_user)


@router.put("/{user_id}", response_model=SingleUserFullResponse)
async def update_user(
    user_id: uuid.UUID,
    request_data: UserUpdateRequest,
    current_user: User = Depends(require_admin_or_root),
    service: UserService = Depends(get_user_service),
):
    """### [Admin/Root] Update data user (nama, role, password)."""
    updated = await service.update_user(user_id=user_id, data=request_data, current_user=current_user)
    return SingleUserFullResponse(message="User berhasil diperbarui.", data=updated)


@router.delete("/{user_id}", response_model=BaseSingleResponse, status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: uuid.UUID,
    current_user: User = Depends(require_admin_or_root),
    service: UserService = Depends(get_user_service),
):
    """### [Admin/Root] Hapus user. Tidak bisa hapus akun sendiri atau akun root."""
    await service.delete_user(user_id=user_id, current_user=current_user)
    return BaseSingleResponse(message="User berhasil dihapus.")
