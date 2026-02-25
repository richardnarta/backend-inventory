# app/di/deps.py
from fastapi import Depends, HTTPException, status, Request
from jose import JWTError, jwt
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List

from app.core.database import get_db
from app.core.config import settings
from app.model.user import User, UserRole
from app.repository.user import UserRepository


async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    
    credentials_exception = HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        "Could not validate credentials",
        {"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None: raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_repo = UserRepository(db)
    user = await user_repo.get_by_username(username=username)
    if user is None: raise credentials_exception
        
    return user


def require_roles(*allowed_roles: UserRole):
    """
    Factory yang menghasilkan FastAPI dependency untuk membatasi akses berdasarkan role.
    Contoh penggunaan: Depends(require_roles(UserRole.root, UserRole.admin))
    """
    async def _guard(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Akses ditolak. Diperlukan role: {[r.value for r in allowed_roles]}."
            )
        return current_user
    return _guard


# --- Shorthand dependencies siap pakai ---

def require_admin_or_root(current_user: User = Depends(get_current_user)) -> User:
    """Hanya root dan admin yang bisa mengakses. Digunakan untuk user management."""
    if current_user.role not in (UserRole.root, UserRole.admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak. Hanya admin dan root yang dapat mengakses fitur ini."
        )
    return current_user


def require_write_access(current_user: User = Depends(get_current_user)) -> User:
    """Staff tidak bisa melakukan operasi tulis (POST/PUT/DELETE)."""
    if current_user.role == UserRole.staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak. Staff hanya memiliki akses read-only."
        )
    return current_user