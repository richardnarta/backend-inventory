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

    async def bulk_delete(self, ids: Optional[list], delete_all: bool) -> BaseSingleResponse:
        """Bulk delete inventory items by list of kode_barang or delete all"""
        from sqlmodel import select, delete as sql_delete
        from app.model.inventory import Inventory

        if delete_all:
            # Delete all inventories
            all_items, _ = await self.inventory_repo.get_all(page=1, limit=999999)
            deleted_count = 0
            for item in all_items:
                await self.inventory_repo.delete(db_inventory=item)
                deleted_count += 1
            return BaseSingleResponse(
                message=f"Berhasil menghapus semua {deleted_count} data barang."
            )
        elif ids:
            deleted_count = 0
            not_found = []
            for kode in ids:
                item = await self.inventory_repo.get_by_id(kode_barang=kode)
                if item:
                    await self.inventory_repo.delete(db_inventory=item)
                    deleted_count += 1
                else:
                    not_found.append(kode)
            msg = f"Berhasil menghapus {deleted_count} data barang."
            if not_found:
                msg += f" Tidak ditemukan: {', '.join(not_found)}."
            return BaseSingleResponse(message=msg)
        else:
            raise HTTPException(
                status_code=400,
                detail="Harap berikan ids atau set delete_all=true."
            )
    
    async def batch_upload_from_excel(self, items_data: list) -> dict:
        """
        Batch upload inventory items from Excel data.
        
        Args:
            items_data: List of dictionaries containing inventory item data
            
        Returns:
            Dictionary with upload statistics
        """
        successful_count = 0
        duplicate_count = 0
        errors = []
        
        for item_data in items_data:
            try:
                # Check if item already exists
                existing_item = await self.inventory_repo.get_by_id(
                    kode_barang=item_data['kode_barang']
                )
                
                if existing_item:
                    # Skip duplicates
                    duplicate_count += 1
                    errors.append({"kode_barang": item_data['kode_barang'], "reason": "Kode barang sudah ada (duplikat)."})
                    continue
                
                # Create new inventory item
                db_inventory = Inventory(**item_data)
                await self.inventory_repo.create(db_inventory=db_inventory)
                successful_count += 1
                
            except Exception as e:
                # Skip items that fail to create
                errors.append({"kode_barang": item_data.get('kode_barang', 'Unknown'), "reason": f"Gagal menyimpan ke database: {str(e)}"})
                continue
        
        return {
            "successful_count": successful_count,
            "duplicate_count": duplicate_count,
            "errors": errors
        }