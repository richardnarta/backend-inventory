from __future__ import annotations
from pydantic import BaseModel, computed_field
from typing import Optional
from app.schema.base_response import BaseSingleResponse, BaseListResponse
from app.schema.buyer.response import BuyerData

# Data Transfer Object
class AccountReceivableData(BaseModel):
    id: int
    period: str
    age_0_30_days: Optional[float] = 0
    age_31_60_days: Optional[float] = 0
    age_61_90_days: Optional[float] = 0
    age_over_90_days: Optional[float] = 0
    buyer: Optional[BuyerData] = None

    @computed_field
    @property
    def total(self) -> float:
        return (
            (self.age_0_30_days or 0) +
            (self.age_31_60_days or 0) +
            (self.age_61_90_days or 0) +
            (self.age_over_90_days or 0)
        )

    class Config:
        from_attributes = True

# Response Schemas
class SingleAccountReceivableResponse(BaseSingleResponse):
    data: AccountReceivableData

class BulkAccountReceivableResponse(BaseListResponse[AccountReceivableData]):
    pass