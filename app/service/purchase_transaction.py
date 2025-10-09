from typing import Optional
from datetime import date
from fastapi import HTTPException, status

from app.model.inventory import InventoryType
from app.repository.purchase_transaction import PurchaseTransactionRepository
from app.repository.inventory import InventoryRepository
from app.repository.supplier import SupplierRepository
from app.schema.purchase_transaction.request import (
    PurchaseTransactionCreateRequest,
    PurchaseTransactionUpdateRequest,
)
from app.schema.purchase_transaction.response import (
    BulkPurchaseTransactionResponse,
    SinglePurchaseTransactionResponse,
)
from app.schema.base_response import BaseSingleResponse

class PurchaseTransactionService:
    """Service class for purchase transaction-related business logic."""

    def __init__(
        self,
        pt_repo: PurchaseTransactionRepository,
        inventory_repo: InventoryRepository,
        supplier_repo: SupplierRepository,
    ):
        self.pt_repo = pt_repo
        self.inventory_repo = inventory_repo
        self.supplier_repo = supplier_repo

    async def get_all(
        self,
        page: int,
        limit: int,
        supplier_id: Optional[int] = None,
        inventory_id: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        inventory_type: Optional[InventoryType] = None,
    ) -> BulkPurchaseTransactionResponse:
        """Retrieves a paginated list of purchase transactions."""
        items, total_count = await self.pt_repo.get_all(
            page=page,
            limit=limit,
            supplier_id=supplier_id,
            inventory_id=inventory_id,
            start_date=start_date,
            end_date=end_date,
            inventory_type=inventory_type,
        )
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0

        return BulkPurchaseTransactionResponse(
            items=items,
            item_count=total_count,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )

    async def get_by_id(self, pt_id: int) -> SinglePurchaseTransactionResponse:
        """Retrieves a single purchase transaction by its ID."""
        transaction = await self.pt_repo.get_by_id(pt_id=pt_id)
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaksi pembelian tidak ditemukan.",
            )
        return SinglePurchaseTransactionResponse(data=transaction)

    async def create(
        self, pt_create: PurchaseTransactionCreateRequest
    ) -> SinglePurchaseTransactionResponse:
        """
        Creates a new purchase transaction and increases inventory stock.
        """
        # Validate foreign keys
        supplier = await self.supplier_repo.get_by_id(supplier_id=pt_create.supplier_id)
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Supplier tidak ditemukan.",
            )
        
        inventory = await self.inventory_repo.get_by_id(inventory_id=pt_create.inventory_id)
        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Barang (inventory) tidak ditemukan.",
            )
        
        # Business Logic: Increase inventory stock
        inventory.roll_count = (inventory.roll_count or 0) + (pt_create.roll_count or 0)
        inventory.weight_kg = (inventory.weight_kg or 0) + (pt_create.weight_kg or 0)
        inventory.bale_count = (inventory.bale_count or 0) + (pt_create.bale_count or 0)

        new_transaction = await self.pt_repo.create(pt_create=pt_create)
        return SinglePurchaseTransactionResponse(
            message="Berhasil mencatat transaksi pembelian.", data=new_transaction
        )

    async def update(
        self, pt_id: int, pt_update: PurchaseTransactionUpdateRequest
    ) -> SinglePurchaseTransactionResponse:
        """
        Updates a purchase transaction and adjusts inventory stock accordingly.
        """
        db_transaction = await self.pt_repo.get_by_id(pt_id=pt_id)
        if not db_transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaksi pembelian tidak ditemukan.",
            )
        
        # Business Logic: Adjust inventory stock based on the difference
        inventory = await self.inventory_repo.get_by_id(inventory_id=db_transaction.inventory_id)
        if not inventory:
             raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Barang (inventory) terkait transaksi ini tidak ditemukan, update dibatalkan.",
            )

        # Calculate differences
        roll_diff = (pt_update.roll_count or db_transaction.roll_count) - (db_transaction.roll_count or 0)
        weight_diff = (pt_update.weight_kg or db_transaction.weight_kg) - (db_transaction.weight_kg or 0)
        bale_diff = (pt_update.bale_count or db_transaction.bale_count) - (db_transaction.bale_count or 0)

        # Apply differences to stock
        inventory.roll_count = (inventory.roll_count or 0) + roll_diff
        inventory.weight_kg = (inventory.weight_kg or 0) + weight_diff
        inventory.bale_count = (inventory.bale_count or 0) + bale_diff
        
        updated_transaction = await self.pt_repo.update(
            db_pt=db_transaction, pt_update=pt_update
        )
        return SinglePurchaseTransactionResponse(
            message="Berhasil mengupdate transaksi pembelian.", data=updated_transaction
        )

    async def delete(self, pt_id: int) -> BaseSingleResponse:
        """
        Deletes a purchase transaction and reverses its effect on inventory stock.
        """
        db_transaction = await self.pt_repo.get_by_id(pt_id=pt_id)
        if not db_transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaksi pembelian tidak ditemukan.",
            )
        
        # Business Logic: Revert inventory stock changes
        inventory = await self.inventory_repo.get_by_id(inventory_id=db_transaction.inventory_id)
        if inventory:
            inventory.roll_count = (inventory.roll_count or 0) - (db_transaction.roll_count or 0)
            inventory.weight_kg = (inventory.weight_kg or 0) - (db_transaction.weight_kg or 0)
            inventory.bale_count = (inventory.bale_count or 0) - (db_transaction.bale_count or 0)

        await self.pt_repo.delete(db_pt=db_transaction)
        return BaseSingleResponse(
            message=f"Berhasil menghapus transaksi pembelian dengan id {pt_id}."
        )