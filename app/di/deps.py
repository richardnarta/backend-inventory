# app/di/deps.py
from fastapi import Depends, HTTPException, status, Request
from jose import JWTError, jwt
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.model.user import User
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
        print(payload)
        username: str = payload.get("sub")
        if username is None: raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_repo = UserRepository(db)
    user = await user_repo.get_by_username(username=username)
    if user is None: raise credentials_exception
        
    return user