from pydantic import BaseModel
from typing import Optional
from .base import BaseListResponse, BaseSingleResponse

class MachineData(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
        
class SingleMachineResponse(BaseSingleResponse):
    data: MachineData
    
class BulkMachineResponse(BaseListResponse[MachineData]):
    pass