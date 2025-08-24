from typing import Optional, Dict, Any
from datetime import date
from fastapi import HTTPException, status

from app.repository.transaction import SalesTransactionRepository
from app.repository.buyer import BuyerRepository
from app.repository.inventory import InventoryRepository
# The Pydantic request models
from app.schema.request.transaction import SalesTransactionCreateRequest, SalesTransactionUpdateRequest
# The Pydantic response models
from app.schema.response.transaction import (
    BulkSalesTransactionResponse, 
    SingleSalesTransactionResponse,
    BaseSingleResponse
)

class SalesTransactionService:
    """Service class for sales transaction-related business logic using Pydantic."""

    def __init__(
        self, 
        transaction_repo: SalesTransactionRepository, 
        buyer_repo: BuyerRepository, 
        inventory_repo: InventoryRepository
    ):
        self.transaction_repo = transaction_repo
        self.buyer_repo = buyer_repo
        self.inventory_repo = inventory_repo

    async def get_all(
        self, 
        buyer_id: Optional[int], 
        inventory_id: Optional[str], 
        start_date: Optional[date], 
        end_date: Optional[date], 
        page: int, 
        limit: int
    ) -> BulkSalesTransactionResponse:
        """
        Retrieves a paginated list of transactions and formats the response.
        """
        items, total_count = await self.transaction_repo.get_all(
            buyer_id=buyer_id,
            inventory_id=inventory_id,
            start_date=start_date,
            end_date=end_date,
            page=page, 
            limit=limit
        )
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0
        
        return BulkSalesTransactionResponse(
            items=items,
            item_count=total_count,
            page=page,
            limit=limit,
            total_pages=total_pages
        )

    async def get_by_id(self, transaction_id: int) -> SingleSalesTransactionResponse:
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
        return SingleSalesTransactionResponse(data=transaction)

    async def create(self, data: SalesTransactionCreateRequest) -> SingleSalesTransactionResponse:
        """
        Creates a new transaction.
        """
        item_dict = data.model_dump()
        
        # Check fk availability
        buyer = await self.buyer_repo.get_by_id(item_dict.get('buyer_id'))
        if not buyer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pembeli tidak ditemukan."
            )
            
        inventory = await self.inventory_repo.get_by_id(item_dict.get('inventory_id'))
        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Barang tidak ditemukan."
            )
        
        new_transaction = await self.transaction_repo.create(item_dict)
        return SingleSalesTransactionResponse(
            message="Berhasil menambahkan transaksi.",
            data=new_transaction
        )

    async def update(self, transaction_id: int, data: SalesTransactionUpdateRequest) -> SingleSalesTransactionResponse:
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
        buyer = await self.buyer_repo.get_by_id(update_dict.get('buyer_id'))
        if not buyer and update_dict.get('buyer_id'):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pembeli tidak ditemukan."
            )
            
        inventory = await self.inventory_repo.get_by_id(update_dict.get('inventory_id'))
        if not inventory and update_dict.get('inventory_id'):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Barang tidak ditemukan."
            )
        
        updated_transaction = await self.transaction_repo.update(transaction_id, update_dict)
        return SingleSalesTransactionResponse(
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
