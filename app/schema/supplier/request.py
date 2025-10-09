from pydantic import BaseModel
from typing import Optional

class SupplierCreateRequest(BaseModel):
    name: str
    phone_num: Optional[str] = None
    address: Optional[str] = None
    note: Optional[str] = None

class SupplierUpdateRequest(BaseModel):
    name: Optional[str] = None
    phone_num: Optional[str] = None
    address: Optional[str] = None
    note: Optional[str] = None