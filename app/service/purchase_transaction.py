from typing import Optional
from datetime import date
from fastapi import HTTPException, status

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
    ) -> BulkPurchaseTransactionResponse:
        """Retrieves a paginated list of purchase transactions."""
        items, total_count = await self.pt_repo.get_all(
            page=page,
            limit=limit,
            supplier_id=supplier_id,
            inventory_id=inventory_id,
            start_date=start_date,
            end_date=end_date,
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
        Creates a purchase transaction and automatically updates inventory stock.
        Handles unit conversion if transaction unit differs from inventory unit.
        """
        # Validate supplier if provided
        if pt_create.supplier_id:
            supplier = await self.supplier_repo.get_by_id(supplier_id=pt_create.supplier_id)
            if not supplier:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Supplier tidak ditemukan."
                )

        # Validate inventory item
        inventory_item = await self.inventory_repo.get_by_id(kode_barang=pt_create.inventory_id)
        if not inventory_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item inventory tidak ditemukan."
            )

        # Prepare data for repository (auto-calculation of total_price handled by repository)
        pt_create_data = pt_create.model_dump()
        
        # Create transaction (repository will auto-calculate total_price if not provided)
        new_transaction = await self.pt_repo.create(pt_create_data=pt_create_data)
        
        # AUTO-UPDATE INVENTORY STOCK with unit conversion
        from app.utils.unit_converter import add_quantity_to_inventory
        
        new_quantity = add_quantity_to_inventory(
            inventory_quantity=inventory_item.quantity,
            inventory_unit=inventory_item.quantity_unit,
            add_quantity=pt_create.quantity,
            add_unit=pt_create.quantity_unit
        )
        
        # Update inventory with new quantity (keeping original unit)
        await self.inventory_repo.update_by_kode(
            kode_barang=inventory_item.kode_barang,
            update_data={"quantity": new_quantity}
        )
        
        created_transaction = await self.pt_repo.get_by_id(pt_id=new_transaction.id)

        return SinglePurchaseTransactionResponse(
            message="Berhasil membuat data transaksi pembelian dan memperbarui stok inventory.",
            data=created_transaction
        )

    async def update(
        self, pt_id: int, pt_update: PurchaseTransactionUpdateRequest
    ) -> SinglePurchaseTransactionResponse:
        """
        Updates a purchase transaction with automatic stock adjustment.
        If quantity/unit changes, reverses old stock change and applies new one.
        """
        db_transaction = await self.pt_repo.get_by_id(pt_id=pt_id)
        if not db_transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaksi pembelian tidak ditemukan.",
            )
        
        # Validate supplier if being updated
        if pt_update.supplier_id is not None:
            supplier = await self.supplier_repo.get_by_id(supplier_id=pt_update.supplier_id)
            if not supplier:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Supplier tidak ditemukan."
                )
        
        # Validate inventory if being updated
        new_inventory_id = pt_update.inventory_id if pt_update.inventory_id is not None else db_transaction.inventory_id
        inventory_item = await self.inventory_repo.get_by_id(kode_barang=new_inventory_id)
        if not inventory_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item inventory tidak ditemukan."
            )
        
        # Check if quantity/unit changed - need stock adjustment
        quantity_changed = (pt_update.quantity is not None and pt_update.quantity != db_transaction.quantity)
        unit_changed = (pt_update.quantity_unit is not None and pt_update.quantity_unit != db_transaction.quantity_unit)
        inventory_changed = (pt_update.inventory_id is not None and pt_update.inventory_id != db_transaction.inventory_id)
        
        if quantity_changed or unit_changed or inventory_changed:
            from app.utils.unit_converter import subtract_quantity_from_inventory, add_quantity_to_inventory
            
            # STEP 1: Rollback old transaction (subtract old quantity from current stock)
            old_inventory = inventory_item if not inventory_changed else await self.inventory_repo.get_by_id(kode_barang=db_transaction.inventory_id)
            if old_inventory:
                rollback_quantity = subtract_quantity_from_inventory(
                    inventory_quantity=old_inventory.quantity,
                    inventory_unit=old_inventory.quantity_unit,
                    subtract_quantity=db_transaction.quantity,
                    subtract_unit=db_transaction.quantity_unit
                )
                await self.inventory_repo.update_by_kode(
                    kode_barang=old_inventory.kode_barang,
                    update_data={"quantity": rollback_quantity}
                )
            
            # STEP 2: Apply new transaction (add new quantity)
            new_quantity = pt_update.quantity if pt_update.quantity is not None else db_transaction.quantity
            new_unit = pt_update.quantity_unit if pt_update.quantity_unit is not None else db_transaction.quantity_unit
            
            # Reload inventory to get latest quantity after rollback
            inventory_item = await self.inventory_repo.get_by_id(kode_barang=new_inventory_id)
            updated_stock = add_quantity_to_inventory(
                inventory_quantity=inventory_item.quantity,
                inventory_unit=inventory_item.quantity_unit,
                add_quantity=new_quantity,
                add_unit=new_unit
            )
            await self.inventory_repo.update_by_kode(
                kode_barang=inventory_item.kode_barang,
                update_data={"quantity": updated_stock}
            )
        
        updated_transaction = await self.pt_repo.update(
            db_pt=db_transaction, pt_update=pt_update
        )
        return SinglePurchaseTransactionResponse(
            message="Berhasil mengupdate transaksi pembelian dan menyesuaikan stok.", 
            data=updated_transaction
        )

    async def delete(self, pt_id: int) -> BaseSingleResponse:
        """
        Deletes a purchase transaction with automatic stock rollback.
        Subtracts the transaction quantity from inventory.
        """
        db_transaction = await self.pt_repo.get_by_id(pt_id=pt_id)
        if not db_transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaksi pembelian tidak ditemukan.",
            )
        
        # ROLLBACK STOCK: Subtract transaction quantity from inventory
        from app.utils.unit_converter import subtract_quantity_from_inventory
        
        inventory_item = await self.inventory_repo.get_by_id(kode_barang=db_transaction.inventory_id)
        if inventory_item:
            rollback_quantity = subtract_quantity_from_inventory(
                inventory_quantity=inventory_item.quantity,
                inventory_unit=inventory_item.quantity_unit,
                subtract_quantity=db_transaction.quantity,
                subtract_unit=db_transaction.quantity_unit
            )
            await self.inventory_repo.update_by_kode(
                kode_barang=inventory_item.kode_barang,
                update_data={"quantity": rollback_quantity}
            )

        await self.pt_repo.delete(db_pt=db_transaction)
        return BaseSingleResponse(
            message=f"Berhasil menghapus transaksi pembelian dengan id {pt_id} dan rollback stok."
        )