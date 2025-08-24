from typing import Optional
from fastapi import HTTPException, status

from app.repository.buyer import BuyerRepository
from app.model.buyer import Buyer # The DB model
# The Pydantic request models
from app.schema.request.buyer import BuyerCreateRequest, BuyerUpdateRequest
# The Pydantic response models
from app.schema.response.buyer import (
    BulkBuyerResponse, 
    SingleBuyerResponse,
    BaseSingleResponse
)

class BuyerService:
    """Service class for buyer-related business logic using Pydantic."""

    def __init__(self, buyer_repo: BuyerRepository):
        self.buyer_repo = buyer_repo

    async def get_all(self, name: Optional[str], page: int, limit: int) -> BulkBuyerResponse:
        """
        Retrieves a paginated list of buyers and formats the response.
        """
        items, total_count = await self.buyer_repo.get_all(name=name, page=page, limit=limit)
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0
        
        return BulkBuyerResponse(
            items=items,
            item_count=total_count,
            page=page,
            limit=limit,
            total_pages=total_pages
        )

    async def get_by_id(self, buyer_id: int) -> SingleBuyerResponse:
        """
        Retrieves a single buyer by their ID.
        Raises an HTTPException if the buyer is not found.
        """
        buyer = await self.buyer_repo.get_by_id(buyer_id)
        if not buyer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pembeli tidak ditemukan."
            )
        return SingleBuyerResponse(data=buyer)

    async def create(self, data: BuyerCreateRequest) -> SingleBuyerResponse:
        """
        Creates a new buyer.
        """
        item_dict = data.model_dump()
        new_buyer = await self.buyer_repo.create(item_dict)
        return SingleBuyerResponse(
            message="Berhasil menambahkan pembeli.",
            data=new_buyer
        )

    async def update(self, buyer_id: int, data: BuyerUpdateRequest) -> SingleBuyerResponse:
        """
        Updates an existing buyer.
        Raises an HTTPException if the buyer is not found.
        """
        buyer = await self.buyer_repo.get_by_id(buyer_id)
        if not buyer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pembeli tidak ditemukan."
            )
            
        update_dict = data.model_dump(exclude_unset=True)
        updated_buyer = await self.buyer_repo.update(buyer_id, update_dict)
        return SingleBuyerResponse(
            message="Berhasil mengupdate data pembeli.",
            data=updated_buyer
        )

    async def delete(self, buyer_id: int) -> BaseSingleResponse:
        """
        Deletes a buyer.
        Raises an HTTPException if the buyer is not found.
        """
        deleted_buyer = await self.buyer_repo.delete(buyer_id)
        if not deleted_buyer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pembeli tidak ditemukan."
            )
        return BaseSingleResponse(message=f"Berhasil menghapus pembeli dengan id {buyer_id}.")
