from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from app.schema.base_response import BaseSingleResponse, BaseListResponse

# Data Transfer Object (Matches new Inventory model)
class InventoryData(BaseModel):
    kode_barang: str
    nama_barang: str
    quantity: float
    quantity_unit: str
    additional_note: str
    harga_modal: float
    harga_jual_eceran: float
    harga_jual_grosir: float

    class Config:
        from_attributes = True

# Response Schemas
class SingleInventoryResponse(BaseSingleResponse):
    data: InventoryData

class BulkInventoryResponse(BaseListResponse[InventoryData]):
    pass