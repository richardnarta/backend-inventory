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
    """Service class for sales transaction-related business logic with multi-item support."""

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
        Creates a sales transaction with multiple items and automatically updates inventory stock.
        Validates stock availability for ALL items before creating transaction.
        """
        # Validate buyer if provided
        if st_create.buyer_id:
            buyer = await self.buyer_repo.get_by_id(buyer_id=st_create.buyer_id)
            if not buyer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Buyer tidak ditemukan."
                )

        # Validate all inventory items AND check stock availability
        inventory_items = {}
        insufficient_items = []
        
        for item in st_create.items:
            inventory_item = await self.inventory_repo.get_by_id(kode_barang=item.inventory_id)
            if not inventory_item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Item inventory '{item.inventory_id}' tidak ditemukan."
                )
            
            # Check stock availability
            if inventory_item.quantity < item.quantity:
                insufficient_items.append({
                    "kode_barang": item.inventory_id,
                    "nama_barang": inventory_item.nama_barang,
                    "available": inventory_item.quantity,
                    "requested": item.quantity,
                    "unit": inventory_item.quantity_unit
                })
            
            inventory_items[item.inventory_id] = inventory_item

        # If any item has insufficient stock, reject the entire transaction
        if insufficient_items:
            error_details = "; ".join([
                f"{item['nama_barang']} (tersedia: {item['available']} {item['unit']}, diminta: {item['requested']} {item['unit']})"
                for item in insufficient_items
            ])
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stok tidak mencukupi untuk item: {error_details}"
            )

        # Create transaction header
        header_data = {
            "transaction_date": st_create.transaction_date,
            "buyer_id": st_create.buyer_id,
            "notes": st_create.notes,
            "total_amount": 0.0  # Will be calculated from items
        }
        transaction_header = await self.st_repo.create_header(header_data)

        # Create items and update stock
        total_amount = 0.0
        for item_request in st_create.items:
            inventory_item = inventory_items[item_request.inventory_id]
            
            # Calculate subtotal
            subtotal = item_request.quantity * item_request.price_per_unit
            total_amount += subtotal
            
            # Create item with inventory's quantity_unit
            item_data = {
                "sales_transaction_id": transaction_header.id,
                "inventory_id": item_request.inventory_id,
                "quantity": item_request.quantity,
                "quantity_unit": inventory_item.quantity_unit,  # Use inventory's unit
                "price_per_unit": item_request.price_per_unit,
                "subtotal": subtotal
            }
            await self.st_repo.create_item(item_data)
            
            # AUTO-UPDATE INVENTORY STOCK (subtract quantity)
            new_quantity = inventory_item.quantity - item_request.quantity
            await self.inventory_repo.update_by_kode(
                kode_barang=inventory_item.kode_barang,
                update_data={"quantity": new_quantity}
            )

        # Update header with total_amount
        await self.st_repo.update_header(
            transaction_header,
            {"total_amount": total_amount}
        )

        # Reload transaction with all relationships
        created_transaction = await self.st_repo.get_by_id(st_id=transaction_header.id)

        return SingleSalesTransactionResponse(
            message="Berhasil membuat transaksi penjualan dengan multiple items dan memperbarui stok inventory.",
            data=created_transaction
        )

    async def update(
        self, st_id: int, st_update: SalesTransactionUpdateRequest
    ) -> SingleSalesTransactionResponse:
        """
        Updates a sales transaction with automatic stock adjustment.
        Rollbacks old items stock and applies new items stock.
        """
        # Get existing transaction
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

        # STEP 1: Rollback stock for all old items
        for old_item in db_transaction.items:
            if old_item.inventory_id:
                inventory_item = await self.inventory_repo.get_by_id(kode_barang=old_item.inventory_id)
                if inventory_item:
                    rollback_quantity = inventory_item.quantity + old_item.quantity
                    await self.inventory_repo.update_by_kode(
                        kode_barang=inventory_item.kode_barang,
                        update_data={"quantity": rollback_quantity}
                    )

        # STEP 2: Delete all old items
        await self.st_repo.delete_all_items(st_id)

        # STEP 3: Create new items if provided
        total_amount = 0.0
        if st_update.items:
            # Validate all inventory items AND check stock
            inventory_items = {}
            insufficient_items = []
            
            for item in st_update.items:
                inventory_item = await self.inventory_repo.get_by_id(kode_barang=item.inventory_id)
                if not inventory_item:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Item inventory '{item.inventory_id}' tidak ditemukan."
                    )
                
                # Check stock (after rollback)
                if inventory_item.quantity < item.quantity:
                    insufficient_items.append({
                        "kode_barang": item.inventory_id,
                        "nama_barang": inventory_item.nama_barang,
                        "available": inventory_item.quantity,
                        "requested": item.quantity,
                        "unit": inventory_item.quantity_unit
                    })
                
                inventory_items[item.inventory_id] = inventory_item

            # If any item has insufficient stock, reject
            if insufficient_items:
                error_details = "; ".join([
                    f"{item['nama_barang']} (tersedia: {item['available']} {item['unit']}, diminta: {item['requested']} {item['unit']})"
                    for item in insufficient_items
                ])
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Stok tidak mencukupi setelah rollback untuk item: {error_details}"
                )

            # Create new items and update stock
            for item_request in st_update.items:
                inventory_item = inventory_items[item_request.inventory_id]
                
                # Calculate subtotal
                subtotal = item_request.quantity * item_request.price_per_unit
                total_amount += subtotal
                
                # Create item
                item_data = {
                    "sales_transaction_id": st_id,
                    "inventory_id": item_request.inventory_id,
                    "quantity": item_request.quantity,
                    "quantity_unit": inventory_item.quantity_unit,
                    "price_per_unit": item_request.price_per_unit,
                    "subtotal": subtotal
                }
                await self.st_repo.create_item(item_data)
                
                # AUTO-UPDATE INVENTORY STOCK (subtract new quantity)
                new_quantity = inventory_item.quantity - item_request.quantity
                await self.inventory_repo.update_by_kode(
                    kode_barang=inventory_item.kode_barang,
                    update_data={"quantity": new_quantity}
                )

        # STEP 4: Update header
        update_data = {}
        if st_update.transaction_date is not None:
            update_data["transaction_date"] = st_update.transaction_date
        if st_update.buyer_id is not None:
            update_data["buyer_id"] = st_update.buyer_id
        if st_update.notes is not None:
            update_data["notes"] = st_update.notes
        if st_update.items:
            update_data["total_amount"] = total_amount

        if update_data:
            await self.st_repo.update_header(db_transaction, update_data)

        # Reload transaction
        updated_transaction = await self.st_repo.get_by_id(st_id=st_id)
        
        return SingleSalesTransactionResponse(
            message="Berhasil mengupdate transaksi penjualan dan menyesuaikan stok.",
            data=updated_transaction
        )

    async def delete(self, st_id: int) -> BaseSingleResponse:
        """
        Deletes a sales transaction with automatic stock rollback for all items.
        """
        db_transaction = await self.st_repo.get_by_id(st_id=st_id)
        if not db_transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaksi penjualan tidak ditemukan.",
            )

        # ROLLBACK STOCK: Add back all items quantity to inventory
        for item in db_transaction.items:
            if item.inventory_id:
                inventory_item = await self.inventory_repo.get_by_id(kode_barang=item.inventory_id)
                if inventory_item:
                    rollback_quantity = inventory_item.quantity + item.quantity
                    await self.inventory_repo.update_by_kode(
                        kode_barang=inventory_item.kode_barang,
                        update_data={"quantity": rollback_quantity}
                    )

        # Delete transaction (will cascade delete items)
        await self.st_repo.delete(db_st=db_transaction)
        
        return BaseSingleResponse(
            message=f"Berhasil menghapus transaksi penjualan dengan id {st_id} dan rollback stok untuk {len(db_transaction.items)} item(s)."
        )