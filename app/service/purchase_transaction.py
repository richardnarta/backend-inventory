from typing import Optional
from datetime import date
from fastapi import HTTPException, status

from app.model.inventory import InventoryType
from app.repository.purchase_transaction import PurchaseTransactionRepository
from app.repository.inventory import InventoryRepository
from app.repository.supplier import SupplierRepository
from app.repository.knitting_process import KnittingProcessRepository
from app.schema.purchase_transaction.request import (
    PurchaseTransactionCreateRequest,
    PurchaseTransactionUpdateRequest,
)
from app.schema.purchase_transaction.response import (
    BulkPurchaseTransactionResponse,
    SinglePurchaseTransactionResponse,
)
from app.schema.base_response import BaseSingleResponse

BALE_TO_KG_RATIO = 181.44

class PurchaseTransactionService:
    """Service class for purchase transaction-related business logic."""

    def __init__(
        self,
        pt_repo: PurchaseTransactionRepository,
        inventory_repo: InventoryRepository,
        supplier_repo: SupplierRepository,
        kp_repo: KnittingProcessRepository,
    ):
        self.pt_repo = pt_repo
        self.inventory_repo = inventory_repo
        self.supplier_repo = supplier_repo
        self.kp_repo = kp_repo

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
        Creates a purchase transaction, calculates and sets its bale_count,
        and updates the corresponding inventory stock.
        """
        supplier = await self.supplier_repo.get_by_id(supplier_id=pt_create.supplier_id)
        if not supplier:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier tidak ditemukan.")

        inventory_item = await self.inventory_repo.get_by_id(inventory_id=pt_create.inventory_id)
        if not inventory_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item inventory tidak ditemukan.")

        # --- Logika Kalkulasi dan Persiapan Data ---
        pt_create_data = pt_create.model_dump()
        
        if inventory_item.type == InventoryType.THREAD:
            bale_increase = round(pt_create.weight_kg / BALE_TO_KG_RATIO, 3)
            
            # 1. Update stok inventory
            current_weight = inventory_item.weight_kg or 0
            current_bales = inventory_item.bale_count or 0
            inventory_item.weight_kg = round(current_weight + pt_create.weight_kg, 3)
            inventory_item.bale_count = round(current_bales + bale_increase, 3)
            
            # 2. Tambahkan bale_count ke data transaksi yang akan dibuat
            pt_create_data['bale_count'] = bale_increase
        
        elif inventory_item.type == InventoryType.FABRIC:
            current_weight = inventory_item.weight_kg or 0
            current_rolls = inventory_item.roll_count or 0
            inventory_item.weight_kg = round(current_weight + pt_create.weight_kg, 3)
            inventory_item.roll_count = round(current_rolls + pt_create.roll_count, 3)
        
        # Kirim dictionary yang sudah lengkap ke repository
        new_transaction = await self.pt_repo.create(pt_create_data=pt_create_data)
        created_transaction = await self.pt_repo.get_by_id(pt_id=new_transaction.id)

        return SinglePurchaseTransactionResponse(
            message="Berhasil membuat data transaksi pembelian.",
            data=created_transaction
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
        Deletion is prevented if the item is a thread allocated to a pending knit process.
        """
        db_transaction = await self.pt_repo.get_by_id(pt_id=pt_id)
        if not db_transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaksi pembelian tidak ditemukan.",
            )
        
        # Validasi alokasi pada proses rajut yang sedang berjalan (TETAP DI SINI)
        inventory = await self.inventory_repo.get_by_id(inventory_id=db_transaction.inventory_id)
        if inventory and inventory.type == InventoryType.THREAD:
            allocated_thread_ids = await self.kp_repo.get_all_pending_material_ids()
            if db_transaction.inventory_id in allocated_thread_ids:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Hapus gagal: Barang '{inventory.name}' sedang dialokasikan untuk proses rajut yang berjalan."
                )

        # Logika rollback stok
        if inventory:
            weight_to_revert = db_transaction.weight_kg or 0
            
            if (inventory.weight_kg or 0) < weight_to_revert:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Hapus gagal: Stok '{inventory.name}' tidak mencukupi untuk dikembalikan."
                )
            inventory.weight_kg = round((inventory.weight_kg or 0) - weight_to_revert, 3)

            if inventory.type == InventoryType.THREAD:
                bale_decrease = db_transaction.bale_count or 0
                if (inventory.bale_count or 0) < bale_decrease:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"Hapus gagal: Stok bale '{inventory.name}' tidak mencukupi untuk dikembalikan."
                    )
                inventory.bale_count = round((inventory.bale_count or 0) - bale_decrease, 3)

            elif inventory.type == InventoryType.FABRIC:
                rolls_to_revert = db_transaction.roll_count or 0
                if (inventory.roll_count or 0) < rolls_to_revert:
                         raise HTTPException(
                            status_code=status.HTTP_409_CONFLICT,
                            detail=f"Hapus gagal: Stok roll '{inventory.name}' tidak mencukupi untuk dikembalikan."
                        )
                inventory.roll_count = round((inventory.roll_count or 0) - rolls_to_revert, 3)

        await self.pt_repo.delete(db_pt=db_transaction)
        return BaseSingleResponse(
            message=f"Berhasil menghapus transaksi pembelian dengan id {pt_id} dan mengembalikan stok."
        )