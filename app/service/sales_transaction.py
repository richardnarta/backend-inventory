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
        Creates a sales transaction and automatically updates inventory stock.
        Handles unit conversion if transaction unit differs from inventory unit.
        Validates sufficient stock before processing.
        """
        # Validate buyer if provided
        if st_create.buyer_id:
            buyer = await self.buyer_repo.get_by_id(buyer_id=st_create.buyer_id)
            if not buyer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Buyer tidak ditemukan."
                )

        # Validate inventory item
        inventory_item = await self.inventory_repo.get_by_id(kode_barang=st_create.inventory_id)
        if not inventory_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item inventory tidak ditemukan."
            )
        
        # Check stock availability with unit conversion
        from app.utils.unit_converter import convert_quantity, subtract_quantity_from_inventory
        
        # Convert sales quantity to inventory unit for validation
        sales_qty_in_inventory_unit = convert_quantity(
            quantity=st_create.quantity,
            from_unit=st_create.quantity_unit,
            to_unit=inventory_item.quantity_unit
        )
        
        if inventory_item.quantity < sales_qty_in_inventory_unit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stok tidak mencukupi. Tersedia: {inventory_item.quantity} {inventory_item.quantity_unit.value}, "
                       f"diminta: {sales_qty_in_inventory_unit:.2f} {inventory_item.quantity_unit.value} "
                       f"(dari {st_create.quantity} {st_create.quantity_unit.value})"
            )

        # Create transaction (repository will auto-calculate total_price if not provided)
        new_transaction = await self.st_repo.create(st_create=st_create)
        
        # AUTO-UPDATE INVENTORY STOCK with unit conversion
        new_quantity = subtract_quantity_from_inventory(
            inventory_quantity=inventory_item.quantity,
            inventory_unit=inventory_item.quantity_unit,
            subtract_quantity=st_create.quantity,
            subtract_unit=st_create.quantity_unit
        )
        
        # Update inventory with new quantity (keeping original unit)
        await self.inventory_repo.update_by_kode(
            kode_barang=inventory_item.kode_barang,
            update_data={"quantity": new_quantity}
        )
        
        created_transaction = await self.st_repo.get_by_id(st_id=new_transaction.id)

        return SingleSalesTransactionResponse(
            message="Berhasil membuat data transaksi penjualan dan memperbarui stok inventory.",
            data=created_transaction
        )

    async def update(
        self, st_id: int, st_update: SalesTransactionUpdateRequest
    ) -> SingleSalesTransactionResponse:
        """
        Updates a sales transaction with automatic stock adjustment.
        If quantity/unit changes, reverses old stock change and applies new one.
        """
        db_transaction = await self.st_repo.get_by_id(st_id=st_id)
        if not db_transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaksi penjualan tidak ditemukan.",
            )
        
        # Validate buyer if being updated
        if st_update.buyer_id is not None:
            buyer = await self.buyer_repo.get_by_id(buyer_id=st_update.buyer_id)
            if not buyer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Buyer tidak ditemukan."
                )
        
        # Validate inventory if being updated
        new_inventory_id = st_update.inventory_id if st_update.inventory_id is not None else db_transaction.inventory_id
        inventory_item = await self.inventory_repo.get_by_id(kode_barang=new_inventory_id)
        if not inventory_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item inventory tidak ditemukan."
            )
        
        # Check if quantity/unit changed - need stock adjustment
        quantity_changed = (st_update.quantity is not None and st_update.quantity != db_transaction.quantity)
        unit_changed = (st_update.quantity_unit is not None and st_update.quantity_unit != db_transaction.quantity_unit)
        inventory_changed = (st_update.inventory_id is not None and st_update.inventory_id != db_transaction.inventory_id)
        
        if quantity_changed or unit_changed or inventory_changed:
            from app.utils.unit_converter import add_quantity_to_inventory, subtract_quantity_from_inventory, convert_quantity
            
            # STEP 1: Rollback old transaction (add back old quantity to current stock)
            old_inventory = inventory_item if not inventory_changed else await self.inventory_repo.get_by_id(kode_barang=db_transaction.inventory_id)
            if old_inventory:
                rollback_quantity = add_quantity_to_inventory(
                    inventory_quantity=old_inventory.quantity,
                    inventory_unit=old_inventory.quantity_unit,
                    add_quantity=db_transaction.quantity,
                    add_unit=db_transaction.quantity_unit
                )
                await self.inventory_repo.update_by_kode(
                    kode_barang=old_inventory.kode_barang,
                    update_data={"quantity": rollback_quantity}
                )
            
            # STEP 2: Apply new transaction (subtract new quantity)
            new_quantity = st_update.quantity if st_update.quantity is not None else db_transaction.quantity
            new_unit = st_update.quantity_unit if st_update.quantity_unit is not None else db_transaction.quantity_unit
            
            # Reload inventory to get latest quantity after rollback
            inventory_item = await self.inventory_repo.get_by_id(kode_barang=new_inventory_id)
            
            # Validate stock availability
            new_qty_in_inventory_unit = convert_quantity(
                quantity=new_quantity,
                from_unit=new_unit,
                to_unit=inventory_item.quantity_unit
            )
            
            if inventory_item.quantity < new_qty_in_inventory_unit:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Stok tidak mencukupi setelah rollback. Tersedia: {inventory_item.quantity} {inventory_item.quantity_unit.value}, "
                           f"diminta: {new_qty_in_inventory_unit:.2f} {inventory_item.quantity_unit.value}"
                )
            
            updated_stock = subtract_quantity_from_inventory(
                inventory_quantity=inventory_item.quantity,
                inventory_unit=inventory_item.quantity_unit,
                subtract_quantity=new_quantity,
                subtract_unit=new_unit
            )
            await self.inventory_repo.update_by_kode(
                kode_barang=inventory_item.kode_barang,
                update_data={"quantity": updated_stock}
            )
        
        updated_transaction = await self.st_repo.update(
            db_st=db_transaction, st_update=st_update
        )
        return SingleSalesTransactionResponse(
            message="Berhasil mengupdate transaksi penjualan dan menyesuaikan stok.",
            data=updated_transaction
        )

    async def delete(self, st_id: int) -> BaseSingleResponse:
        """
        Deletes a sales transaction with automatic stock rollback.
        Adds back the transaction quantity to inventory.
        """
        db_transaction = await self.st_repo.get_by_id(st_id=st_id)
        if not db_transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaksi penjualan tidak ditemukan.",
            )
        
        # ROLLBACK STOCK: Add back transaction quantity to inventory
        from app.utils.unit_converter import add_quantity_to_inventory
        
        inventory_item = await self.inventory_repo.get_by_id(kode_barang=db_transaction.inventory_id)
        if inventory_item:
            rollback_quantity = add_quantity_to_inventory(
                inventory_quantity=inventory_item.quantity,
                inventory_unit=inventory_item.quantity_unit,
                add_quantity=db_transaction.quantity,
                add_unit=db_transaction.quantity_unit
            )
            await self.inventory_repo.update_by_kode(
                kode_barang=inventory_item.kode_barang,
                update_data={"quantity": rollback_quantity}
            )

        await self.st_repo.delete(db_st=db_transaction)
        return BaseSingleResponse(
            message=f"Berhasil menghapus transaksi penjualan dengan id {st_id} dan rollback stok."
        )