# app/service/inventory.py

from typing import Optional
from fastapi import HTTPException, status

from app.repository.inventory import InventoryRepository
from app.model.inventory import Inventory
from app.schema.inventory.request import InventoryCreateRequest, InventoryUpdateRequest
from app.schema.inventory.response import (
    BulkInventoryResponse,
    SingleInventoryResponse,
)
from app.schema.base_response import BaseSingleResponse

class InventoryService:
    def __init__(self, inventory_repo: InventoryRepository):
        self.inventory_repo = inventory_repo

    async def get_all(
        self,
        nama_barang: Optional[str],
        kode_barang: Optional[str],
        quantity_unit: Optional[str],
        page: int,
        limit: int,
    ) -> BulkInventoryResponse:
        """Get all inventory items with optional filters and pagination"""
        items, total_count = await self.inventory_repo.get_all(
            nama_barang=nama_barang,
            kode_barang=kode_barang,
            quantity_unit=quantity_unit,
            page=page,
            limit=limit
        )
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0

        return BulkInventoryResponse(
            items=items,
            item_count=total_count,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )

    async def get_by_id(self, kode_barang: str) -> SingleInventoryResponse:
        """Get a single inventory item by kode_barang"""
        inventory = await self.inventory_repo.get_by_id(kode_barang=kode_barang)
        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Barang dengan kode '{kode_barang}' tidak ditemukan.",
            )
        return SingleInventoryResponse(data=inventory)

    async def create(
        self, inventory_create: InventoryCreateRequest
    ) -> SingleInventoryResponse:
        """Create a new inventory item"""
        # Check if item with this kode_barang already exists
        existing_item = await self.inventory_repo.get_by_id(
            kode_barang=inventory_create.kode_barang
        )
        if existing_item:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Barang dengan kode '{inventory_create.kode_barang}' sudah ada.",
            )

        # Create new inventory item
        db_inventory = Inventory.model_validate(inventory_create)
        new_inventory = await self.inventory_repo.create(db_inventory=db_inventory)
        
        return SingleInventoryResponse(
            message="Berhasil menambahkan data barang.", 
            data=new_inventory
        )

    async def update(
        self, kode_barang: str, inventory_update: InventoryUpdateRequest
    ) -> SingleInventoryResponse:
        """Update an existing inventory item"""
        db_inventory = await self.inventory_repo.get_by_id(kode_barang=kode_barang)
        if not db_inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Barang dengan kode '{kode_barang}' tidak ditemukan.",
            )

        updated_inventory = await self.inventory_repo.update(
            db_inventory=db_inventory, 
            inventory_update=inventory_update
        )
        
        return SingleInventoryResponse(
            message="Berhasil mengupdate data barang.", 
            data=updated_inventory
        )

    async def delete(self, kode_barang: str) -> BaseSingleResponse:
        """Delete an inventory item"""
        db_inventory = await self.inventory_repo.get_by_id(kode_barang=kode_barang)
        if not db_inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Barang dengan kode '{kode_barang}' tidak ditemukan.",
            )

        await self.inventory_repo.delete(db_inventory=db_inventory)
        
        return BaseSingleResponse(
            message=f"Berhasil menghapus data barang dengan kode {kode_barang}."
        )