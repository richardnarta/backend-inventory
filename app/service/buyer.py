from typing import Optional
from fastapi import HTTPException, status

from app.repository.buyer import BuyerRepository
from app.schema.buyer.request import BuyerCreateRequest, BuyerUpdateRequest
from app.schema.buyer.response import (
    BulkBuyerResponse,
    SingleBuyerResponse,
    BuyerData, # Import BuyerData
)
from app.schema.base_response import BaseSingleResponse

class BuyerService:
    """Service class for buyer-related business logic."""

    def __init__(self, buyer_repo: BuyerRepository):
        self.buyer_repo = buyer_repo

    async def get_all(
        self,
        name: Optional[str],
        page: int,
        limit: int,
    ) -> BulkBuyerResponse:
        """
        Retrieves a paginated list of buyers and formats the response.
        """
        # The repository now returns a list of (Buyer, is_risked) tuples
        items_with_risk, total_count = await self.buyer_repo.get_all(
            name=name, page=page, limit=limit
        )
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0
        
        # Map the repository result to the BuyerData response schema
        response_items = []
        for buyer, is_risked in items_with_risk:
            buyer_data = BuyerData.model_validate(buyer)
            buyer_data.is_risked = is_risked
            response_items.append(buyer_data)

        return BulkBuyerResponse(
            items=response_items,
            item_count=total_count,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )

    async def get_by_id(self, buyer_id: int) -> SingleBuyerResponse:
        """
        Retrieves a single buyer by their ID.
        """
        # The repository now returns a (Buyer, is_risked) tuple
        result = await self.buyer_repo.get_by_id(buyer_id=buyer_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pembeli tidak ditemukan.",
            )
        
        buyer, is_risked = result
        
        # Map the result to the BuyerData response schema
        response_data = BuyerData.model_validate(buyer)
        response_data.is_risked = is_risked
        
        return SingleBuyerResponse(data=response_data)

    async def create(self, buyer_create: BuyerCreateRequest) -> SingleBuyerResponse:
        # Create method doesn't need the is_risked flag, so no changes here
        new_buyer = await self.buyer_repo.create(buyer_create=buyer_create)
        
        # For consistency, we wrap it in the new response model (is_risked will be default False)
        response_data = BuyerData.model_validate(new_buyer)
        
        return SingleBuyerResponse(
            message="Berhasil menambahkan data pembeli.", data=response_data
        )

    async def update(
        self, buyer_id: int, buyer_update: BuyerUpdateRequest
    ) -> SingleBuyerResponse:
        # We need to fetch the original buyer object first for the update method
        result = await self.buyer_repo.get_by_id(buyer_id=buyer_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pembeli tidak ditemukan.",
            )
        
        db_buyer, is_risked = result # is_risked from the initial fetch
        
        updated_buyer = await self.buyer_repo.update(
            db_buyer=db_buyer, buyer_update=buyer_update
        )

        # Map the final result to the response schema
        response_data = BuyerData.model_validate(updated_buyer)
        response_data.is_risked = is_risked # Use the risk status from before the update
        
        return SingleBuyerResponse(
            message="Berhasil mengupdate data pembeli.", data=response_data
        )

    async def delete(self, buyer_id: int) -> BaseSingleResponse:
        # We need to fetch the original buyer object first for the delete method
        result = await self.buyer_repo.get_by_id(buyer_id=buyer_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pembeli tidak ditemukan.",
            )
        
        db_buyer, _ = result

        await self.buyer_repo.delete(db_buyer=db_buyer)
        return BaseSingleResponse(
            message=f"Berhasil menghapus data pembeli dengan id {buyer_id}."
        )