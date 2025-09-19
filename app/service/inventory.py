from typing import Optional, List, Tuple
from fastapi import HTTPException, status

from app.repository.inventory import InventoryRepository
from app.model.inventory import Inventory # The DB model
# The Pydantic request models
from app.schema.request.inventory import InventoryCreateRequest, InventoryUpdateRequest
# The Pydantic response models
from app.schema.response.inventory import (
    BulkInventoryResponse, 
    SingleInventoryResponse,
    BaseSingleResponse
)

class InventoryService:
    """Service class for inventory-related business logic using Pydantic."""

    def __init__(self, inventory_repo: InventoryRepository):
        self.inventory_repo = inventory_repo

    async def get_all(self, name: Optional[str], type: Optional[str], id: Optional[str], page: int, limit: int) -> BulkInventoryResponse:
        """
        Retrieves a paginated list of inventory items and formats the response.
        """
        items, total_count = await self.inventory_repo.get_all(name=name, id=id, type=type, page=page, limit=limit)
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0
        
        return BulkInventoryResponse(
            items=items,
            item_count=total_count,
            page=page,
            limit=limit,
            total_pages=total_pages
        )

    async def get_by_id(self, item_id: str) -> SingleInventoryResponse:
        """
        Retrieves a single inventory item by its ID.
        Raises an HTTPException if the item is not found.
        """
        inventory_item = await self.inventory_repo.get_by_id(item_id)
        if not inventory_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Barang tidak ditemukan."
            )
        return SingleInventoryResponse(data=inventory_item)

    async def create(self, data: InventoryCreateRequest) -> SingleInventoryResponse:
        """
        Creates a new inventory item.
        """
        item_dict = data.model_dump()
        inventory = await self.inventory_repo.get_by_id(item_dict.get('id'))
        if inventory:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Id barang telah digunakan."
            )
        new_item = await self.inventory_repo.create(item_dict)
        
        return SingleInventoryResponse(
            message="Berhasil menambahkan barang.",
            data=new_item
        )

    async def update(self, item_id: str, data: InventoryUpdateRequest) -> SingleInventoryResponse:
        """
        Updates an existing inventory item.
        Raises an HTTPException if the item is not found.
        """
        inventory_item = await self.inventory_repo.get_by_id(item_id)
        if not inventory_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Barang tidak ditemukan."
            )
            
        update_dict = data.model_dump(exclude_unset=True)
        updated_item = await self.inventory_repo.update(item_id, update_dict)
        return SingleInventoryResponse(
            message="Berhasil mengupdate data barang.",
            data=updated_item
        )

    async def delete(self, item_id: str) -> BaseSingleResponse:
        """
        Deletes an inventory item.
        Raises an HTTPException if the item is not found.
        """
        deleted_item = await self.inventory_repo.delete(item_id)
        if not deleted_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Barang tidak ditemukan."
            )
        return BaseSingleResponse(message=f"Berhasil menghapus barang dengan id {item_id}.")
