from pydantic import BaseModel, field_validator
from typing import Optional
from app.model.user import UserRole

class UserCreateByAdminRequest(BaseModel):
    nama: str
    username: str
    password: str
    role: Optional[UserRole] = UserRole.staff

    @field_validator('password')
    def validate_password_length(cls, v: str) -> str:
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password tidak boleh lebih dari 72 karakter.')
        return v

class UserUpdateRequest(BaseModel):
    nama: Optional[str] = None
    role: Optional[UserRole] = None
    password: Optional[str] = None

    @field_validator('password')
    def validate_password_length(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v.encode('utf-8')) > 72:
            raise ValueError('Password tidak boleh lebih dari 72 karakter.')
        return v
