from typing import Optional, Dict, Any
from datetime import date
from fastapi import HTTPException, status

from app.repository.purchase_transaction import PurchaseTransactionRepository
from app.repository.supplier import SupplierRepository
from app.repository.inventory import InventoryRepository
# The Pydantic request models
from app.schema.request.purchase_transaction import PurchaseTransactionCreateRequest, PurchaseTransactionUpdateRequest
# The Pydantic response models
from app.schema.response.purchase_transaction import (
    BulkPurchaseTransactionResponse, 
    SinglePurchaseTransactionResponse,
    BaseSingleResponse
)

class PurchaseTransactionService:
    """Service class for purchase transaction-related business logic using Pydantic."""

    def __init__(
        self, 
        transaction_repo: PurchaseTransactionRepository, 
        supplier_repo: SupplierRepository, 
        inventory_repo: InventoryRepository
    ):
        self.transaction_repo = transaction_repo
        self.supplier_repo = supplier_repo
        self.inventory_repo = inventory_repo

    async def get_all(
        self, 
        supplier_id: Optional[int], 
        inventory_id: Optional[str], 
        start_date: Optional[date], 
        end_date: Optional[date],
        dyed: Optional[bool],
        page: int, 
        limit: int
    ) -> BulkPurchaseTransactionResponse:
        """
        Retrieves a paginated list of transactions and formats the response.
        """
        items, total_count = await self.transaction_repo.get_all(
            supplier_id=supplier_id,
            inventory_id=inventory_id,
            start_date=start_date,
            end_date=end_date,
            dyed=dyed,
            page=page, 
            limit=limit
        )
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0
        
        return BulkPurchaseTransactionResponse(
            items=items,
            item_count=total_count,
            page=page,
            limit=limit,
            total_pages=total_pages
        )

    async def get_by_id(self, transaction_id: int) -> SinglePurchaseTransactionResponse:
        """
        Retrieves a single transaction by its ID.
        Raises an HTTPException if the transaction is not found.
        """
        transaction = await self.transaction_repo.get_by_id(transaction_id)
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaksi tidak ditemukan."
            )
        return SinglePurchaseTransactionResponse(data=transaction)

    async def create(self, data: PurchaseTransactionCreateRequest) -> SinglePurchaseTransactionResponse:
        """
        Creates a new transaction.
        """
        item_dict = data.model_dump()
        
        # Check fk availability
        supplier = await self.supplier_repo.get_by_id(item_dict.get('supplier_id'))
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Supplier tidak ditemukan."
            )
            
        inventory = await self.inventory_repo.get_by_id(item_dict.get('inventory_id'))
        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Barang tidak ditemukan."
            )
        
        new_transaction = await self.transaction_repo.create(item_dict)
        return SinglePurchaseTransactionResponse(
            message="Berhasil menambahkan transaksi.",
            data=new_transaction
        )

    async def update(self, transaction_id: int, data: PurchaseTransactionUpdateRequest) -> SinglePurchaseTransactionResponse:
        """
        Updates an existing transaction.
        Raises an HTTPException if the transaction is not found.
        """
        transaction = await self.transaction_repo.get_by_id(transaction_id)
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaksi tidak ditemukan."
            )
            
        update_dict = data.model_dump(exclude_unset=True)
        
        # Check fk availability
        supplier = await self.supplier_repo.get_by_id(update_dict.get('supplier_id'))
        if not supplier and update_dict.get('supplier_id'):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Supplier tidak ditemukan."
            )
            
        inventory = await self.inventory_repo.get_by_id(update_dict.get('inventory_id'))
        if not inventory and update_dict.get('inventory_id'):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Barang tidak ditemukan."
            )
        
        updated_transaction = await self.transaction_repo.update(transaction_id, update_dict)
        return SinglePurchaseTransactionResponse(
            message="Berhasil mengupdate data transaksi.",
            data=updated_transaction
        )

    async def delete(self, transaction_id: int) -> BaseSingleResponse:
        """
        Deletes a transaction.
        Raises an HTTPException if the transaction is not found.
        """
        deleted_transaction = await self.transaction_repo.delete(transaction_id)
        if not deleted_transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaksi tidak ditemukan."
            )
        return BaseSingleResponse(message=f"Berhasil menghapus transaksi dengan id {transaction_id}.")
