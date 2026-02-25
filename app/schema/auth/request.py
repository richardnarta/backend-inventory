from pydantic import BaseModel, field_validator
from typing import Optional
from app.model.user import UserRole

class UserLoginRequest(BaseModel):
    username: str
    password: str

class UserCreateRequest(BaseModel):
    nama: str
    username: str
    password: str
    role: Optional[UserRole] = UserRole.staff
    
    @field_validator('password')
    def validate_password_length(cls, v: str) -> str:
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password tidak boleh lebih dari 72 karakter.')
        return v