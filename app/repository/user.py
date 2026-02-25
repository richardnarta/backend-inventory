import uuid
from typing import Optional, List
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.model.user import User

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, *, user_data: User) -> User:
        self.session.add(user_data)
        await self.session.commit()
        await self.session.refresh(user_data)
        return user_data

    async def get_by_username(self, *, username: str) -> Optional[User]:
        statement = select(User).where(User.username == username)
        result = await self.session.execute(statement)
        return result.scalars().one_or_none()

    async def get_by_id(self, *, user_id: uuid.UUID) -> Optional[User]:
        statement = select(User).where(User.id == user_id)
        result = await self.session.execute(statement)
        return result.scalars().one_or_none()

    async def get_all(self, *, skip: int = 0, limit: int = 100) -> List[User]:
        statement = select(User).offset(skip).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def update(self, *, user: User) -> User:
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, *, user: User) -> None:
        await self.session.delete(user)
        await self.session.commit()