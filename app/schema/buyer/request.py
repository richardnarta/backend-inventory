from pydantic import BaseModel
from typing import Optional

class BuyerCreateRequest(BaseModel):
    name: str
    phone_num: Optional[str] = None
    address: Optional[str] = None
    note: Optional[str] = None

class BuyerUpdateRequest(BaseModel):
    name: Optional[str] = None
    phone_num: Optional[str] = None
    address: Optional[str] = None
    note: Optional[str] = None