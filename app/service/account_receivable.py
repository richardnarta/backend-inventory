from typing import Optional
from fastapi import HTTPException, status

from app.repository.account_receivable import AccountReceivableRepository
from app.repository.buyer import BuyerRepository
# The Pydantic request models
from app.schema.request.account_receivable import AccountReceivableCreateRequest, AccountReceivableUpdateRequest
# The Pydantic response models
from app.schema.response.account_receivable import (
    BulkAccountReceivableResponse, 
    SingleAccountReceivableResponse,
    BaseSingleResponse
)

class AccountReceivableService:
    """Service class for account receivable-related business logic using Pydantic."""

    def __init__(
        self, 
        receivable_repo: AccountReceivableRepository,
        buyer_repo: BuyerRepository
    ):
        self.receivable_repo = receivable_repo
        self.buyer_repo = buyer_repo

    async def get_all(
        self, 
        buyer_id: Optional[int], 
        period: Optional[str], 
        page: int, 
        limit: int
    ) -> BulkAccountReceivableResponse:
        """
        Retrieves a paginated list of account receivables and formats the response.
        """
        items, total_count = await self.receivable_repo.get_all(
            buyer_id=buyer_id,
            period=period,
            page=page, 
            limit=limit
        )
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0
        
        return BulkAccountReceivableResponse(
            items=items,
            item_count=total_count,
            page=page,
            limit=limit,
            total_pages=total_pages
        )

    async def get_by_id(self, receivable_id: int) -> SingleAccountReceivableResponse:
        """
        Retrieves a single account receivable by its ID.
        Raises an HTTPException if the record is not found.
        """
        receivable = await self.receivable_repo.get_by_id(receivable_id)
        if not receivable:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data piutang tidak ditemukan."
            )
        return SingleAccountReceivableResponse(data=receivable)

    async def create(self, data: AccountReceivableCreateRequest) -> SingleAccountReceivableResponse:
        """
        Creates a new account receivable.
        """
        item_dict = data.model_dump()
        
        # Check fk availability
        buyer = await self.buyer_repo.get_by_id(item_dict.get('buyer_id'))
        if not buyer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pembeli tidak ditemukan."
            )
        
        new_receivable = await self.receivable_repo.create(item_dict)
        return SingleAccountReceivableResponse(
            message="Berhasil menambahkan data piutang.",
            data=new_receivable
        )

    async def update(self, receivable_id: int, data: AccountReceivableUpdateRequest) -> SingleAccountReceivableResponse:
        """
        Updates an existing account receivable.
        Raises an HTTPException if the record is not found.
        """
        receivable = await self.receivable_repo.get_by_id(receivable_id)
        if not receivable:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data piutang tidak ditemukan."
            )
            
        update_dict = data.model_dump(exclude_unset=True)
        
        # Check fk availability
        buyer = await self.buyer_repo.get_by_id(update_dict.get('buyer_id'))
        if not buyer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pembeli tidak ditemukan."
            )
        
        updated_receivable = await self.receivable_repo.update(receivable_id, update_dict)
        return SingleAccountReceivableResponse(
            message="Berhasil mengupdate data piutang.",
            data=updated_receivable
        )

    async def delete(self, receivable_id: int) -> BaseSingleResponse:
        """
        Deletes an account receivable.
        Raises an HTTPException if the record is not found.
        """
        deleted_receivable = await self.receivable_repo.delete(receivable_id)
        if not deleted_receivable:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data piutang tidak ditemukan."
            )
        return BaseSingleResponse(message=f"Berhasil menghapus data piutang dengan id {receivable_id}.")
