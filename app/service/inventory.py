# app/service/inventory_service.py

from typing import Optional
from fastapi import HTTPException, status

from app.repository.inventory import InventoryRepository, BALE_TO_KG_RATIO
from app.model.inventory import Inventory, InventoryType
from app.schema.inventory.request import InventoryCreateRequest, InventoryUpdateRequest
from app.schema.inventory.response import (
    BulkInventoryResponse,
    SingleInventoryResponse,
)
from app.schema.base_response import BaseSingleResponse

class InventoryService:
    # ... (metode __init__, get_all, get_by_id tidak berubah) ...
    def __init__(self, inventory_repo: InventoryRepository):
        self.inventory_repo = inventory_repo

    async def get_all(
        self,
        name: Optional[str],
        id: Optional[str],
        type: Optional[str],
        page: int,
        limit: int,
    ) -> BulkInventoryResponse:
        items, total_count = await self.inventory_repo.get_all(
            name=name, id=id, type=type, page=page, limit=limit
        )
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0

        return BulkInventoryResponse(
            items=items,
            item_count=total_count,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )

    async def get_by_id(self, inventory_id: str) -> SingleInventoryResponse:
        inventory = await self.inventory_repo.get_by_id(inventory_id=inventory_id)
        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Barang (inventory) tidak ditemukan.",
            )
        return SingleInventoryResponse(data=inventory)

    async def create(
        self, inventory_create: InventoryCreateRequest
    ) -> SingleInventoryResponse:
        """
        Creates a new inventory item, setting a default bale_ratio and
        calculating the initial bale_count for threads.
        """
        existing_item = await self.inventory_repo.get_by_id(
            inventory_id=inventory_create.id
        )
        if existing_item:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Barang (inventory) dengan ID '{inventory_create.id}' sudah ada.",
            )

        db_inventory = Inventory.model_validate(inventory_create)

        # --- LOGIKA YANG DISEMPURNAKAN ---
        if db_inventory.type == InventoryType.THREAD:
            # Jika user tidak mengisi bale_ratio, atur ke nilai standar
            if not db_inventory.bale_ratio or db_inventory.bale_ratio <= 0:
                db_inventory.bale_ratio = BALE_TO_KG_RATIO
            
            # Lakukan perhitungan awal
            calculated_bales = (db_inventory.weight_kg or 0) / db_inventory.bale_ratio
            db_inventory.bale_count = round(calculated_bales, 3)
        # ---------------------------------------------

        new_inventory = await self.inventory_repo.create(db_inventory=db_inventory)
        return SingleInventoryResponse(
            message="Berhasil menambahkan data barang.", data=new_inventory
        )

    # ... (metode update dan delete tidak perlu diubah dari versi Anda) ...
    async def update(
        self, inventory_id: str, inventory_update: InventoryUpdateRequest
    ) -> SingleInventoryResponse:
        db_inventory = await self.inventory_repo.get_by_id(inventory_id=inventory_id)
        if not db_inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Barang (inventory) tidak ditemukan.",
            )

        updated_inventory = await self.inventory_repo.update(
            db_inventory=db_inventory, inventory_update=inventory_update
        )
        return SingleInventoryResponse(
            message="Berhasil mengupdate data barang.", data=updated_inventory
        )

    async def delete(self, inventory_id: str) -> BaseSingleResponse:
        db_inventory = await self.inventory_repo.get_by_id(inventory_id=inventory_id)
        if not db_inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Barang (inventory) tidak ditemukan.",
            )

        await self.inventory_repo.delete(db_inventory=db_inventory)
        return BaseSingleResponse(
            message=f"Berhasil menghapus data barang dengan id {inventory_id}."
        )