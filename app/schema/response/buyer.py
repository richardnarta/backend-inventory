from pydantic import BaseModel, Field
from typing import Optional
from .base import BaseListResponse, BaseSingleResponse


class BuyerData(BaseModel):
    id: int
    name: str
    phone_num: Optional[str] = None

    class Config:
        from_attributes = True
        
        
class SingleBuyerResponse(BaseSingleResponse):
    data: BuyerData
    
class BulkBuyerResponse(BaseListResponse[BuyerData]):
    pass