import uuid
from typing import List, Optional
from pydantic import BaseModel
from app.model.user import UserRole

class UserItemData(BaseModel):
    id: uuid.UUID
    nama: str
    username: str
    role: UserRole

    class Config:
        from_attributes = True

class UserListResponse(BaseModel):
    message: str = "Berhasil mengambil data user."
    data: List[UserItemData]

class SingleUserFullResponse(BaseModel):
    message: str = "Berhasil."
    data: UserItemData
