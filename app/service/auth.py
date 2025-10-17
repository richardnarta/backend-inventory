from fastapi import HTTPException, status, Response, Request
from datetime import datetime, timedelta, timezone

from app.repository.user import UserRepository
from app.repository.refresh_token import RefreshTokenRepository
from app.schema.auth.request import UserLoginRequest, UserCreateRequest
from app.schema.auth.response import SingleUserResponse, UserData
from app.schema.base_response import BaseSingleResponse
from app.model.user import User
from app.core.security import (
    create_access_token, 
    create_refresh_token, 
    verify_password, 
    hash_password
)
from app.core.config import settings

class AuthService:
    def __init__(self, user_repo: UserRepository, rt_repo: RefreshTokenRepository):
        self.user_repo = user_repo
        self.rt_repo = rt_repo

    async def register(self, *, user_create: UserCreateRequest) -> SingleUserResponse:
        existing_user = await self.user_repo.get_by_username(username=user_create.username)
        if existing_user:
            raise HTTPException(status.HTTP_409_CONFLICT, "Username sudah digunakan.")
        
        hashed_pwd = hash_password(user_create.password)
        user_model = User(
            nama=user_create.nama,
            username=user_create.username,
            hashed_password=hashed_pwd
        )
        new_user = await self.user_repo.create(user_data=user_model)
        return SingleUserResponse(message="Registrasi berhasil.", data=UserData.model_validate(new_user))

    async def login(self, *, form_data: UserLoginRequest, response: Response) -> BaseSingleResponse:
        user = await self.user_repo.get_by_username(username=form_data.username)
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Username atau password salah.")

        access_token = create_access_token(subject=user.username)
        refresh_token = create_refresh_token(subject=user.username)
        
        expires_at = datetime.now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await self.rt_repo.create(token=refresh_token, user_id=user.id, expires_at=expires_at)
        
        PROD = not settings.DEBUG

        response.set_cookie(key="access_token", value=access_token, httponly=True, secure=PROD, samesite="none" if PROD else "lax")
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=PROD, samesite="none" if PROD else "lax")
        
        return BaseSingleResponse(message="Login berhasil.")

    async def logout(self, *, request: Request, response: Response) -> BaseSingleResponse:
        token = request.cookies.get("refresh_token")
        if token:
            await self.rt_repo.delete_by_token(token=token)

        PROD = not settings.DEBUG

        response.delete_cookie(key="access_token", httponly=True, secure=PROD, samesite="none" if PROD else "lax")
        response.delete_cookie("refresh_token", httponly=True, secure=PROD, samesite="none" if PROD else "lax")
        return BaseSingleResponse(message="Logout berhasil.")

    async def refresh(self, *, request: Request, response: Response) -> BaseSingleResponse:
        token = request.cookies.get("refresh_token")
        if not token:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh token tidak ditemukan.")

        db_token = await self.rt_repo.get_by_token(token=token)
        if not db_token or db_token.expires_at < datetime.now():
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh token tidak valid atau sudah kedaluwarsa.")
        
        PROD = not settings.DEBUG
            
        new_access_token = create_access_token(subject=db_token.user.username)

        response.set_cookie(key="access_token", value=new_access_token, httponly=True, secure=PROD, samesite="none" if PROD else "lax")
        return BaseSingleResponse(message="Token berhasil diperbarui.")

    async def get_me(self, *, current_user: User) -> SingleUserResponse:
        return SingleUserResponse(data=UserData.model_validate(current_user))