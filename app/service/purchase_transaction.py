from typing import Optional
from datetime import date, datetime
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
    """Service class for purchase transaction-related business logic with multi-item support."""

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
        Creates a purchase transaction with multiple items and automatically updates inventory stock.
        """
        # Validate supplier if provided
        if pt_create.supplier_id:
            supplier = await self.supplier_repo.get_by_id(supplier_id=pt_create.supplier_id)
            if not supplier:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Supplier tidak ditemukan."
                )

        # Validate all inventory items first
        inventory_items = {}
        for item in pt_create.items:
            inventory_item = await self.inventory_repo.get_by_id(kode_barang=item.inventory_id)
            if not inventory_item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Item inventory '{item.inventory_id}' tidak ditemukan."
                )
            inventory_items[item.inventory_id] = inventory_item

        # Create transaction header
        header_data = {
            "transaction_date": pt_create.transaction_date,
            "supplier_id": pt_create.supplier_id,
            "notes": pt_create.notes,
            "total_amount": 0.0  # Will be calculated from items
        }
        transaction_header = await self.pt_repo.create_header(header_data)

        # Create items and update stock
        total_amount = 0.0
        for item_request in pt_create.items:
            inventory_item = inventory_items[item_request.inventory_id]
            
            # Calculate subtotal
            subtotal = item_request.quantity * item_request.price_per_unit
            total_amount += subtotal
            
            # Create item with inventory's quantity_unit and snapshots
            item_data = {
                "purchase_transaction_id": transaction_header.id,
                "inventory_id": item_request.inventory_id,
                "quantity": item_request.quantity,
                "quantity_unit": inventory_item.quantity_unit,  # Use inventory's unit
                "price_per_unit": item_request.price_per_unit,
                "subtotal": subtotal,
                "item_code_snapshot": inventory_item.kode_barang,
                "item_name_snapshot": inventory_item.nama_barang
            }
            await self.pt_repo.create_item(item_data)
            
            # AUTO-UPDATE INVENTORY STOCK (add quantity)
            new_quantity = inventory_item.quantity + item_request.quantity
            await self.inventory_repo.update_by_kode(
                kode_barang=inventory_item.kode_barang,
                update_data={"quantity": new_quantity}
            )

        # Update header with total_amount
        await self.pt_repo.update_header(
            transaction_header,
            {"total_amount": total_amount}
        )

        # Reload transaction with all relationships
        created_transaction = await self.pt_repo.get_by_id(pt_id=transaction_header.id)

        return SinglePurchaseTransactionResponse(
            message="Berhasil membuat transaksi pembelian dengan multiple items dan memperbarui stok inventory.",
            data=created_transaction
        )

    async def update(
        self, pt_id: int, pt_update: PurchaseTransactionUpdateRequest
    ) -> SinglePurchaseTransactionResponse:
        """
        Updates a purchase transaction with automatic stock adjustment.
        Rollbacks old items stock and applies new items stock.
        """
        # Get existing transaction
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

        # STEP 1: Rollback stock for all old items
        for old_item in db_transaction.items:
            if old_item.inventory_id:
                inventory_item = await self.inventory_repo.get_by_id(kode_barang=old_item.inventory_id)
                if inventory_item:
                    rollback_quantity = inventory_item.quantity - old_item.quantity
                    await self.inventory_repo.update_by_kode(
                        kode_barang=inventory_item.kode_barang,
                        update_data={"quantity": rollback_quantity}
                    )

        # STEP 2: Delete all old items
        await self.pt_repo.delete_all_items(pt_id)

        # STEP 3: Create new items if provided
        total_amount = 0.0
        if pt_update.items:
            # Validate all inventory items
            inventory_items = {}
            for item in pt_update.items:
                inventory_item = await self.inventory_repo.get_by_id(kode_barang=item.inventory_id)
                if not inventory_item:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Item inventory '{item.inventory_id}' tidak ditemukan."
                    )
                inventory_items[item.inventory_id] = inventory_item

            # Create new items and update stock
            for item_request in pt_update.items:
                inventory_item = inventory_items[item_request.inventory_id]
                
                # Calculate subtotal
                subtotal = item_request.quantity * item_request.price_per_unit
                total_amount += subtotal
                
                # Create item with snapshots
                item_data = {
                    "purchase_transaction_id": pt_id,
                    "inventory_id": item_request.inventory_id,
                    "quantity": item_request.quantity,
                    "quantity_unit": inventory_item.quantity_unit,
                    "price_per_unit": item_request.price_per_unit,
                    "subtotal": subtotal,
                    "item_code_snapshot": inventory_item.kode_barang,
                    "item_name_snapshot": inventory_item.nama_barang
                }
                await self.pt_repo.create_item(item_data)
                
                # AUTO-UPDATE INVENTORY STOCK (add new quantity)
                new_quantity = inventory_item.quantity + item_request.quantity
                await self.inventory_repo.update_by_kode(
                    kode_barang=inventory_item.kode_barang,
                    update_data={"quantity": new_quantity}
                )

        # STEP 4: Update header
        update_data = {}
        if pt_update.transaction_date is not None:
            update_data["transaction_date"] = pt_update.transaction_date
        if pt_update.supplier_id is not None:
            update_data["supplier_id"] = pt_update.supplier_id
        if pt_update.notes is not None:
            update_data["notes"] = pt_update.notes
        if pt_update.items:
            update_data["total_amount"] = total_amount

        if update_data:
            await self.pt_repo.update_header(db_transaction, update_data)

        # Reload transaction
        updated_transaction = await self.pt_repo.get_by_id(pt_id=pt_id)
        
        return SinglePurchaseTransactionResponse(
            message="Berhasil mengupdate transaksi pembelian dan menyesuaikan stok.",
            data=updated_transaction
        )

    async def delete(self, pt_id: int) -> BaseSingleResponse:
        """
        Deletes a purchase transaction with automatic stock rollback for all items.
        """
        db_transaction = await self.pt_repo.get_by_id(pt_id=pt_id)
        if not db_transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaksi pembelian tidak ditemukan.",
            )

        # ROLLBACK STOCK: Subtract all items quantity from inventory
        for item in db_transaction.items:
            if item.inventory_id:
                inventory_item = await self.inventory_repo.get_by_id(kode_barang=item.inventory_id)
                if inventory_item:
                    rollback_quantity = inventory_item.quantity - item.quantity
                    await self.inventory_repo.update_by_kode(
                        kode_barang=inventory_item.kode_barang,
                        update_data={"quantity": rollback_quantity}
                    )

        # Delete transaction (will cascade delete items)
        await self.pt_repo.delete(db_pt=db_transaction)
        
        return BaseSingleResponse(
            message=f"Berhasil menghapus transaksi pembelian dengan id {pt_id} dan rollback stok untuk {len(db_transaction.items)} item(s)."
        )

    async def bulk_delete(self, ids: Optional[list], delete_all: bool) -> BaseSingleResponse:
        """Bulk delete purchase transactions, applying stock rollback for each."""
        if delete_all:
            all_items, _ = await self.pt_repo.get_all(page=1, limit=999999)
            deleted_count = 0
            for item in all_items:
                await self.delete(pt_id=item.id)
                deleted_count += 1
            return BaseSingleResponse(
                message=f"Berhasil menghapus semua {deleted_count} transaksi pembelian dan rollback stok."
            )
        elif ids:
            deleted_count = 0
            not_found = []
            for pt_id in ids:
                transaction = await self.pt_repo.get_by_id(pt_id=pt_id)
                if transaction:
                    await self.delete(pt_id=pt_id)
                    deleted_count += 1
                else:
                    not_found.append(str(pt_id))
            msg = f"Berhasil menghapus {deleted_count} transaksi pembelian dan rollback stok."
            if not_found:
                msg += f" Tidak ditemukan id: {', '.join(not_found)}."
            return BaseSingleResponse(message=msg)
        else:
            raise HTTPException(status_code=400, detail="Harap berikan ids atau set delete_all=true.")