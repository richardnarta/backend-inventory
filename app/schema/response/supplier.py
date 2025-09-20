from pydantic import BaseModel
from typing import Optional
from .base import BaseListResponse, BaseSingleResponse


class SupplierData(BaseModel):
    id: int
    name: str
    phone_num: Optional[str] = None

    class Config:
        from_attributes = True
        
        
class SingleSupplierResponse(BaseSingleResponse):
    data: SupplierData
    
class BulkSupplierResponse(BaseListResponse[SupplierData]):
    pass