import uuid
import enum
from typing import List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship, Column
import sqlalchemy as sa

if TYPE_CHECKING:
    from .refresh_token import RefreshToken

class UserRole(str, enum.Enum):
    root  = "root"
    admin = "admin"
    staff = "staff"

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    nama: str
    username: str = Field(unique=True, index=True)
    hashed_password: str
    role: UserRole = Field(
        default=UserRole.staff,
        sa_column=Column(sa.Enum(UserRole, name="userrole"), nullable=False, server_default=UserRole.staff.value)
    )

    refresh_tokens: List["RefreshToken"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )