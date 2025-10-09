from typing import Optional
from datetime import date
from fastapi import HTTPException, status

from app.repository.sales_transaction import SalesTransactionRepository
from app.repository.inventory import InventoryRepository
from app.repository.buyer import BuyerRepository
from app.schema.sales_transaction.request import (
    SalesTransactionCreateRequest,
    SalesTransactionUpdateRequest,
)
from app.schema.sales_transaction.response import (
    BulkSalesTransactionResponse,
    SingleSalesTransactionResponse,
)
from app.schema.base_response import BaseSingleResponse

class SalesTransactionService:
    """Service class for sales transaction-related business logic."""

    def __init__(
        self,
        st_repo: SalesTransactionRepository,
        inventory_repo: InventoryRepository,
        buyer_repo: BuyerRepository,
    ):
        self.st_repo = st_repo
        self.inventory_repo = inventory_repo
        self.buyer_repo = buyer_repo

    async def get_all(
        self,
        page: int,
        limit: int,
        buyer_id: Optional[int] = None,
        inventory_id: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> BulkSalesTransactionResponse:
        """Retrieves a paginated list of sales transactions."""
        items, total_count = await self.st_repo.get_all(
            page=page,
            limit=limit,
            buyer_id=buyer_id,
            inventory_id=inventory_id,
            start_date=start_date,
            end_date=end_date,
        )
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0

        return BulkSalesTransactionResponse(
            items=items,
            item_count=total_count,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )

    async def get_by_id(self, st_id: int) -> SingleSalesTransactionResponse:
        """Retrieves a single sales transaction by its ID."""
        transaction = await self.st_repo.get_by_id(st_id=st_id)
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaksi penjualan tidak ditemukan.",
            )
        return SingleSalesTransactionResponse(data=transaction)

    async def create(
        self, st_create: SalesTransactionCreateRequest
    ) -> SingleSalesTransactionResponse:
        """
        Creates a new sales transaction and decreases inventory stock.
        """
        # Validate foreign keys
        buyer = await self.buyer_repo.get_by_id(buyer_id=st_create.buyer_id)
        if not buyer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pembeli tidak ditemukan.",
            )

        inventory = await self.inventory_repo.get_by_id(inventory_id=st_create.inventory_id)
        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Barang (inventory) tidak ditemukan.",
            )

        # Business Logic: Check for sufficient stock and decrease it
        if (inventory.roll_count or 0) < (st_create.roll_count or 0):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Stok roll tidak mencukupi.")
        if (inventory.weight_kg or 0) < (st_create.weight_kg or 0):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Stok berat (kg) tidak mencukupi.")

        inventory.roll_count -= st_create.roll_count or 0
        inventory.weight_kg -= st_create.weight_kg or 0

        new_transaction = await self.st_repo.create(st_create=st_create)
        return SingleSalesTransactionResponse(
            message="Berhasil mencatat transaksi penjualan.", data=new_transaction
        )

    async def update(
        self, st_id: int, st_update: SalesTransactionUpdateRequest
    ) -> SingleSalesTransactionResponse:
        """
        Updates a sales transaction and adjusts inventory stock accordingly.
        """
        db_transaction = await self.st_repo.get_by_id(st_id=st_id)
        if not db_transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaksi penjualan tidak ditemukan.",
            )

        inventory = await self.inventory_repo.get_by_id(inventory_id=db_transaction.inventory_id)
        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Barang (inventory) terkait transaksi ini tidak ditemukan, update dibatalkan.",
            )

        # Calculate differences to see how the stock should be adjusted
        roll_diff = (st_update.roll_count or db_transaction.roll_count) - (db_transaction.roll_count or 0)
        weight_diff = (st_update.weight_kg or db_transaction.weight_kg) - (db_transaction.weight_kg or 0)

        # Business Logic: Check if stock is sufficient for the change and then adjust
        if (inventory.roll_count or 0) < roll_diff:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Stok roll tidak mencukupi untuk perubahan ini.")
        if (inventory.weight_kg or 0) < weight_diff:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Stok berat (kg) tidak mencukupi untuk perubahan ini.")

        inventory.roll_count -= roll_diff
        inventory.weight_kg -= weight_diff
        
        updated_transaction = await self.st_repo.update(
            db_st=db_transaction, st_update=st_update
        )
        return SingleSalesTransactionResponse(
            message="Berhasil mengupdate transaksi penjualan.", data=updated_transaction
        )

    async def delete(self, st_id: int) -> BaseSingleResponse:
        """
        Deletes a sales transaction and adds the stock back to inventory.
        """
        db_transaction = await self.st_repo.get_by_id(st_id=st_id)
        if not db_transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaksi penjualan tidak ditemukan.",
            )

        # Business Logic: Revert inventory stock changes (add stock back)
        inventory = await self.inventory_repo.get_by_id(inventory_id=db_transaction.inventory_id)
        if inventory:
            inventory.roll_count = (inventory.roll_count or 0) + (db_transaction.roll_count or 0)
            inventory.weight_kg = (inventory.weight_kg or 0) + (db_transaction.weight_kg or 0)

        await self.st_repo.delete(db_st=db_transaction)
        return BaseSingleResponse(
            message=f"Berhasil menghapus transaksi penjualan dengan id {st_id}."
        )