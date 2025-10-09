from typing import Optional
from fastapi import HTTPException, status

from app.repository.inventory import InventoryRepository
from app.schema.inventory.request import InventoryCreateRequest, InventoryUpdateRequest
from app.schema.inventory.response import (
    BulkInventoryResponse,
    SingleInventoryResponse,
)
from app.schema.base_response import BaseSingleResponse

class InventoryService:
    """Service class for inventory-related business logic."""

    def __init__(self, inventory_repo: InventoryRepository):
        """
        Initializes the service with the inventory repository.

        Args:
            inventory_repo: The repository for inventory data.
        """
        self.inventory_repo = inventory_repo

    async def get_all(
        self,
        name: Optional[str],
        id: Optional[str],
        type: Optional[str],
        page: int,
        limit: int,
    ) -> BulkInventoryResponse:
        """
        Retrieves a paginated list of inventory items and formats the response.
        """
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
        """
        Retrieves a single inventory item by its ID.
        Raises an HTTPException if the item is not found.
        """
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
        Creates a new inventory item after validating the ID is unique.
        """
        # Check if an inventory item with this ID already exists
        existing_item = await self.inventory_repo.get_by_id(
            inventory_id=inventory_create.id
        )
        if existing_item:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Barang (inventory) dengan ID '{inventory_create.id}' sudah ada.",
            )

        new_inventory = await self.inventory_repo.create(
            inventory_create=inventory_create
        )
        return SingleInventoryResponse(
            message="Berhasil menambahkan data barang.", data=new_inventory
        )

    async def update(
        self, inventory_id: str, inventory_update: InventoryUpdateRequest
    ) -> SingleInventoryResponse:
        """
        Updates an existing inventory item.
        Raises an HTTPException if the item is not found.
        """
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
        """
        Deletes an inventory item.
        Raises an HTTPException if the item is not found.
        """
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