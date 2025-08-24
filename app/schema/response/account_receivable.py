from pydantic import BaseModel, computed_field
from .base import BaseListResponse, BaseSingleResponse
from .buyer import BuyerData
from typing import Optional


class AccountReceivableData(BaseModel):
    id: int
    buyer: Optional[BuyerData] = None
    period: str
    age_0_30_days: int
    age_31_60_days: int
    age_61_90_days: int
    age_over_90_days: int
    @computed_field
    @property
    def total(self) -> int:
        """Calculates the sum of all age buckets."""
        return (
            self.age_0_30_days + 
            self.age_31_60_days + 
            self.age_61_90_days + 
            self.age_over_90_days
        )

    class Config:
        from_attributes = True
        

class SingleAccountReceivableResponse(BaseSingleResponse):
    data: AccountReceivableData
    

class BulkAccountReceivableResponse(BaseListResponse[AccountReceivableData]):
    pass