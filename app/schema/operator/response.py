from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from app.schema.base_response import BaseSingleResponse, BaseListResponse

# Data Transfer Object
class OperatorData(BaseModel):
    id: int
    name: str
    phone_num: Optional[str] = None

    class Config:
        from_attributes = True

# Response Schemas
class SingleOperatorResponse(BaseSingleResponse):
    data: OperatorData

class BulkOperatorResponse(BaseListResponse[OperatorData]):
    pass