from typing import Optional
from sqlmodel import select, delete
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime
import uuid

from app.model.refresh_token import RefreshToken

class RefreshTokenRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, *, token: str, user_id: uuid.UUID, expires_at: datetime) -> RefreshToken:
        db_token = RefreshToken(token=token, user_id=user_id, expires_at=expires_at)
        self.session.add(db_token)
        await self.session.commit()
        await self.session.refresh(db_token)
        return db_token

    async def get_by_token(self, *, token: str) -> Optional[RefreshToken]:
        statement = select(RefreshToken).where(RefreshToken.token == token).options(
                selectinload(RefreshToken.user),
            )
        result = await self.session.execute(statement)
        return result.scalars().one_or_none()

    async def delete_by_token(self, *, token: str) -> None:
        statement = delete(RefreshToken).where(RefreshToken.token == token)
        await self.session.execute(statement)
        await self.session.commit()