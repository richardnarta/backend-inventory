import uuid
from pydantic import BaseModel
from app.schema.base_response import BaseSingleResponse
from app.model.user import UserRole

# Data Transfer Object (DTO) untuk menampilkan data user secara aman
class UserData(BaseModel):
    id: uuid.UUID
    nama: str
    username: str
    role: UserRole

    class Config:
        from_attributes = True

# Skema respons untuk endpoint /me
class SingleUserResponse(BaseSingleResponse):
    data: UserData