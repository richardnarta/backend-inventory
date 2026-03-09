from typing import Optional
from fastapi import HTTPException, status

from app.repository.buyer import BuyerRepository
from app.schema.buyer.request import BuyerCreateRequest, BuyerUpdateRequest
from app.schema.buyer.response import (
    BulkBuyerResponse,
    SingleBuyerResponse,
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
        """Retrieves a paginated list of buyers"""
        items, total_count = await self.buyer_repo.get_all(
            name=name, page=page, limit=limit
        )
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0

        return BulkBuyerResponse(
            items=items,
            item_count=total_count,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )

    async def get_by_id(self, buyer_id: int) -> SingleBuyerResponse:
        """Retrieves a single buyer by their ID"""
        buyer = await self.buyer_repo.get_by_id(buyer_id=buyer_id)
        if not buyer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pembeli tidak ditemukan.",
            )
        
        return SingleBuyerResponse(data=buyer)

    async def create(self, buyer_create: BuyerCreateRequest) -> SingleBuyerResponse:
        """Create a new buyer"""
        new_buyer = await self.buyer_repo.create(buyer_create=buyer_create)
        
        return SingleBuyerResponse(
            message="Berhasil menambahkan data pembeli.", 
            data=new_buyer
        )

    async def update(
        self, buyer_id: int, buyer_update: BuyerUpdateRequest
    ) -> SingleBuyerResponse:
        """Update an existing buyer"""
        db_buyer = await self.buyer_repo.get_by_id(buyer_id=buyer_id)
        if not db_buyer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pembeli tidak ditemukan.",
            )
        
        updated_buyer = await self.buyer_repo.update(
            db_buyer=db_buyer, buyer_update=buyer_update
        )
        
        return SingleBuyerResponse(
            message="Berhasil mengupdate data pembeli.", 
            data=updated_buyer
        )

    async def delete(self, buyer_id: int) -> BaseSingleResponse:
        """Delete a buyer"""
        db_buyer = await self.buyer_repo.get_by_id(buyer_id=buyer_id)
        if not db_buyer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pembeli tidak ditemukan.",
            )

        await self.buyer_repo.delete(db_buyer=db_buyer)
        return BaseSingleResponse(
            message=f"Berhasil menghapus data pembeli dengan id {buyer_id}."
        )

    async def bulk_delete(self, ids: Optional[list], delete_all: bool) -> BaseSingleResponse:
        """Bulk delete buyers by list of ids or delete all"""
        if delete_all:
            all_items, _ = await self.buyer_repo.get_all(name=None, page=1, limit=999999)
            deleted_count = 0
            for item in all_items:
                await self.buyer_repo.delete(db_buyer=item)
                deleted_count += 1
            return BaseSingleResponse(
                message=f"Berhasil menghapus semua {deleted_count} data pembeli."
            )
        elif ids:
            deleted_count = 0
            not_found = []
            for buyer_id in ids:
                item = await self.buyer_repo.get_by_id(buyer_id=buyer_id)
                if item:
                    await self.buyer_repo.delete(db_buyer=item)
                    deleted_count += 1
                else:
                    not_found.append(str(buyer_id))
            msg = f"Berhasil menghapus {deleted_count} data pembeli."
            if not_found:
                msg += f" Tidak ditemukan id: {', '.join(not_found)}."
            return BaseSingleResponse(message=msg)
        else:
            raise HTTPException(status_code=400, detail="Harap berikan ids atau set delete_all=true.")