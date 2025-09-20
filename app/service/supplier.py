from typing import Optional
from fastapi import HTTPException, status

from app.repository.supplier import SupplierRepository
from app.model.supplier import Supplier # The DB model
# The Pydantic request models
from app.schema.request.supplier import SupplierCreateRequest, SupplierUpdateRequest
# The Pydantic response models
from app.schema.response.supplier import (
    BulkSupplierResponse, 
    SingleSupplierResponse,
    BaseSingleResponse
)

class SupplierService:
    """Service class for supplier-related business logic using Pydantic."""

    def __init__(self, supplier_repo: SupplierRepository):
        self.supplier_repo = supplier_repo

    async def get_all(self, name: Optional[str], page: int, limit: int) -> BulkSupplierResponse:
        """
        Retrieves a paginated list of suppliers and formats the response.
        """
        items, total_count = await self.supplier_repo.get_all(name=name, page=page, limit=limit)
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0
        
        return BulkSupplierResponse(
            items=items,
            item_count=total_count,
            page=page,
            limit=limit,
            total_pages=total_pages
        )

    async def get_by_id(self, supplier_id: int) -> SingleSupplierResponse:
        """
        Retrieves a single supplier by their ID.
        Raises an HTTPException if the supplier is not found.
        """
        supplier = await self.supplier_repo.get_by_id(supplier_id)
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Supplier tidak ditemukan."
            )
        return SingleSupplierResponse(data=supplier)

    async def create(self, data: SupplierCreateRequest) -> SingleSupplierResponse:
        """
        Creates a new supplier.
        """
        item_dict = data.model_dump()
        new_supplier = await self.supplier_repo.create(item_dict)
        return SingleSupplierResponse(
            message="Berhasil menambahkan supplier.",
            data=new_supplier
        )

    async def update(self, supplier_id: int, data: SupplierUpdateRequest) -> SingleSupplierResponse:
        """
        Updates an existing supplier.
        Raises an HTTPException if the supplier is not found.
        """
        supplier = await self.supplier_repo.get_by_id(supplier_id)
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Supplier tidak ditemukan."
            )
            
        update_dict = data.model_dump(exclude_unset=True)
        updated_supplier = await self.supplier_repo.update(supplier_id, update_dict)
        return SingleSupplierResponse(
            message="Berhasil mengupdate data supplier.",
            data=updated_supplier
        )

    async def delete(self, supplier_id: int) -> BaseSingleResponse:
        """
        Deletes a supplier.
        Raises an HTTPException if the supplier is not found.
        """
        deleted_supplier = await self.supplier_repo.delete(supplier_id)
        if not deleted_supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Supplier tidak ditemukan."
            )
        return BaseSingleResponse(message=f"Berhasil menghapus supplier dengan id {supplier_id}.")
