from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from app.schema.base_response import BaseSingleResponse, BaseListResponse

# Data Transfer Object
class SupplierData(BaseModel):
    id: int
    name: str
    phone_num: Optional[str] = None
    address: Optional[str] = None
    note: Optional[str] = None

    class Config:
        from_attributes = True

# Response Schemas
class SingleSupplierResponse(BaseSingleResponse):
    data: SupplierData

class BulkSupplierResponse(BaseListResponse[SupplierData]):
    pass