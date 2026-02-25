import uuid
from typing import Optional, List
from fastapi import HTTPException, status

from app.repository.user import UserRepository
from app.model.user import User, UserRole
from app.core.security import hash_password
from app.schema.user.request import UserCreateByAdminRequest, UserUpdateRequest
from app.schema.user.response import UserItemData

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def list_users(self, *, skip: int = 0, limit: int = 100) -> List[UserItemData]:
        users = await self.user_repo.get_all(skip=skip, limit=limit)
        return [UserItemData.model_validate(u) for u in users]

    async def get_user(self, *, user_id: uuid.UUID) -> UserItemData:
        user = await self.user_repo.get_by_id(user_id=user_id)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User tidak ditemukan.")
        return UserItemData.model_validate(user)

    async def create_user(self, *, data: UserCreateByAdminRequest) -> UserItemData:
        existing = await self.user_repo.get_by_username(username=data.username)
        if existing:
            raise HTTPException(status.HTTP_409_CONFLICT, "Username sudah digunakan.")

        user_model = User(
            nama=data.nama,
            username=data.username,
            hashed_password=hash_password(data.password),
            role=data.role,
        )
        new_user = await self.user_repo.create(user_data=user_model)
        return UserItemData.model_validate(new_user)

    async def update_user(self, *, user_id: uuid.UUID, data: UserUpdateRequest, current_user: User) -> UserItemData:
        user = await self.user_repo.get_by_id(user_id=user_id)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User tidak ditemukan.")

        # Prevent root from being downgraded by a non-root user
        if user.role == UserRole.root and current_user.role != UserRole.root:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Hanya root yang bisa mengubah akun root.")

        if data.nama is not None:
            user.nama = data.nama
        if data.role is not None:
            # Prevent setting role to root unless done by root
            if data.role == UserRole.root and current_user.role != UserRole.root:
                raise HTTPException(status.HTTP_403_FORBIDDEN, "Hanya root yang bisa menetapkan role root.")
            user.role = data.role
        if data.password is not None:
            user.hashed_password = hash_password(data.password)

        updated = await self.user_repo.update(user=user)
        return UserItemData.model_validate(updated)

    async def delete_user(self, *, user_id: uuid.UUID, current_user: User) -> None:
        user = await self.user_repo.get_by_id(user_id=user_id)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User tidak ditemukan.")
        if user.id == current_user.id:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Tidak bisa menghapus akun sendiri.")
        if user.role == UserRole.root:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Akun root tidak dapat dihapus.")
        await self.user_repo.delete(user=user)
