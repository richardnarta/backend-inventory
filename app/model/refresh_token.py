import uuid
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime, timedelta

if TYPE_CHECKING:
    from .user import User

class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_tokens"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(unique=True, index=True)
    expires_at: datetime
    user_id: uuid.UUID = Field(foreign_key="users.id")
    
    user: "User" = Relationship(back_populates="refresh_tokens")