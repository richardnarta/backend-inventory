from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from app.schema.base_response import BaseSingleResponse, BaseListResponse

# Data Transfer Object
class BuyerData(BaseModel):
    id: int
    name: str
    phone_num: Optional[str] = None
    address: Optional[str] = None
    note: Optional[str] = None
    is_risked: bool = False

    class Config:
        from_attributes = True

# Response Schemas
class SingleBuyerResponse(BaseSingleResponse):
    data: BuyerData

class BulkBuyerResponse(BaseListResponse[BuyerData]):
    pass