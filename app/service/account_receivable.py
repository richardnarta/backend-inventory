from typing import Optional
from fastapi import HTTPException, status

from app.repository.account_receivable import AccountReceivableRepository
from app.repository.buyer import BuyerRepository
from app.schema.account_receivable.request import (
    AccountReceivableCreateRequest,
    AccountReceivableUpdateRequest,
)
from app.schema.account_receivable.response import (
    BulkAccountReceivableResponse,
    SingleAccountReceivableResponse,
)
from app.schema.base_response import BaseSingleResponse

class AccountReceivableService:
    """Service class for account receivable-related business logic."""

    def __init__(
        self,
        receivable_repo: AccountReceivableRepository,
        buyer_repo: BuyerRepository,
    ):
        """
        Initializes the service with necessary repositories.

        Args:
            receivable_repo: The repository for account receivable data.
            buyer_repo: The repository for buyer data.
        """
        self.receivable_repo = receivable_repo
        self.buyer_repo = buyer_repo

    async def get_all(
        self,
        buyer_id: Optional[int],
        period: Optional[str],
        page: int,
        limit: int,
    ) -> BulkAccountReceivableResponse:
        """
        Retrieves a paginated list of account receivables and formats the response.
        """
        items, total_count = await self.receivable_repo.get_all(
            buyer_id=buyer_id, period=period, page=page, limit=limit
        )
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0

        return BulkAccountReceivableResponse(
            items=items,
            item_count=total_count,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )

    async def get_by_id(
        self, ar_id: int
    ) -> SingleAccountReceivableResponse:
        """
        Retrieves a single account receivable by its ID.
        Raises an HTTPException if the record is not found.
        """
        receivable = await self.receivable_repo.get_by_id(ar_id=ar_id)
        if not receivable:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data piutang tidak ditemukan.",
            )
        return SingleAccountReceivableResponse(data=receivable)

    async def create(
        self, ar_create: AccountReceivableCreateRequest
    ) -> SingleAccountReceivableResponse:
        """
        Creates a new account receivable after validating the buyer.
        """
        # Check foreign key availability
        buyer = await self.buyer_repo.get_by_id(buyer_id=ar_create.buyer_id)
        if not buyer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pembeli tidak ditemukan.",
            )

        new_receivable = await self.receivable_repo.create(ar_create=ar_create)
        return SingleAccountReceivableResponse(
            message="Berhasil menambahkan data piutang.", data=new_receivable
        )

    async def update(
        self, ar_id: int, ar_update: AccountReceivableUpdateRequest
    ) -> SingleAccountReceivableResponse:
        """
        Updates an existing account receivable.
        Raises an HTTPException if the record is not found or if the new buyer_id is invalid.
        """
        db_receivable = await self.receivable_repo.get_by_id(ar_id=ar_id)
        if not db_receivable:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data piutang tidak ditemukan.",
            )

        # If buyer_id is being updated, check if the new buyer exists
        if ar_update.buyer_id is not None:
            buyer = await self.buyer_repo.get_by_id(buyer_id=ar_update.buyer_id)
            if not buyer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Pembeli tidak ditemukan.",
                )

        updated_receivable = await self.receivable_repo.update(
            db_ar=db_receivable, ar_update=ar_update
        )
        return SingleAccountReceivableResponse(
            message="Berhasil mengupdate data piutang.", data=updated_receivable
        )

    async def delete(self, ar_id: int) -> BaseSingleResponse:
        """
        Deletes an account receivable.
        Raises an HTTPException if the record is not found.
        """
        db_receivable = await self.receivable_repo.get_by_id(ar_id=ar_id)
        if not db_receivable:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data piutang tidak ditemukan.",
            )

        await self.receivable_repo.delete(db_ar=db_receivable)
        return BaseSingleResponse(
            message=f"Berhasil menghapus data piutang dengan id {ar_id}."
        )