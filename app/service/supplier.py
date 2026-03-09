from typing import Optional
from fastapi import HTTPException, status

from app.repository.supplier import SupplierRepository
from app.schema.supplier.request import SupplierCreateRequest, SupplierUpdateRequest
from app.schema.supplier.response import (
    BulkSupplierResponse,
    SingleSupplierResponse,
)
from app.schema.base_response import BaseSingleResponse

class SupplierService:
    """Service class for supplier-related business logic."""

    def __init__(self, supplier_repo: SupplierRepository):
        """
        Initializes the service with the supplier repository.

        Args:
            supplier_repo: The repository for supplier data.
        """
        self.supplier_repo = supplier_repo

    async def get_all(
        self,
        name: Optional[str],
        page: int,
        limit: int,
    ) -> BulkSupplierResponse:
        """
        Retrieves a paginated list of suppliers and formats the response.
        """
        items, total_count = await self.supplier_repo.get_all(
            name=name, page=page, limit=limit
        )
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0

        return BulkSupplierResponse(
            items=items,
            item_count=total_count,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )

    async def get_by_id(self, supplier_id: int) -> SingleSupplierResponse:
        """
        Retrieves a single supplier by their ID.
        Raises an HTTPException if the supplier is not found.
        """
        supplier = await self.supplier_repo.get_by_id(supplier_id=supplier_id)
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Supplier tidak ditemukan.",
            )
        return SingleSupplierResponse(data=supplier)

    async def create(self, supplier_create: SupplierCreateRequest) -> SingleSupplierResponse:
        """
        Creates a new supplier.
        """
        new_supplier = await self.supplier_repo.create(supplier_create=supplier_create)
        return SingleSupplierResponse(
            message="Berhasil menambahkan data supplier.", data=new_supplier
        )

    async def update(
        self, supplier_id: int, supplier_update: SupplierUpdateRequest
    ) -> SingleSupplierResponse:
        """
        Updates an existing supplier.
        Raises an HTTPException if the supplier is not found.
        """
        db_supplier = await self.supplier_repo.get_by_id(supplier_id=supplier_id)
        if not db_supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Supplier tidak ditemukan.",
            )

        updated_supplier = await self.supplier_repo.update(
            db_supplier=db_supplier, supplier_update=supplier_update
        )
        return SingleSupplierResponse(
            message="Berhasil mengupdate data supplier.", data=updated_supplier
        )

    async def delete(self, supplier_id: int) -> BaseSingleResponse:
        """
        Deletes a supplier.
        Raises an HTTPException if the supplier is not found.
        """
        db_supplier = await self.supplier_repo.get_by_id(supplier_id=supplier_id)
        if not db_supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Supplier tidak ditemukan.",
            )

        await self.supplier_repo.delete(db_supplier=db_supplier)
        return BaseSingleResponse(
            message=f"Berhasil menghapus data supplier dengan id {supplier_id}."
        )

    async def bulk_delete(self, ids: Optional[list], delete_all: bool) -> BaseSingleResponse:
        """Bulk delete suppliers by list of ids or delete all"""
        if delete_all:
            all_items, _ = await self.supplier_repo.get_all(name=None, page=1, limit=999999)
            deleted_count = 0
            for item in all_items:
                await self.supplier_repo.delete(db_supplier=item)
                deleted_count += 1
            return BaseSingleResponse(
                message=f"Berhasil menghapus semua {deleted_count} data supplier."
            )
        elif ids:
            deleted_count = 0
            not_found = []
            for supplier_id in ids:
                item = await self.supplier_repo.get_by_id(supplier_id=supplier_id)
                if item:
                    await self.supplier_repo.delete(db_supplier=item)
                    deleted_count += 1
                else:
                    not_found.append(str(supplier_id))
            msg = f"Berhasil menghapus {deleted_count} data supplier."
            if not_found:
                msg += f" Tidak ditemukan id: {', '.join(not_found)}."
            return BaseSingleResponse(message=msg)
        else:
            raise HTTPException(status_code=400, detail="Harap berikan ids atau set delete_all=true.")