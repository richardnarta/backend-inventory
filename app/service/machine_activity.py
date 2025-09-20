from typing import Optional
from datetime import date
from fastapi import HTTPException, status
from app.repository.machine_activity import MachineActivityRepository
from app.repository.inventory import InventoryRepository
from app.repository.machine import MachineRepository
from app.schema.request.machine_activity import MachineActivityCreateRequest, MachineActivityUpdateRequest
from app.schema.response.machine_activity import BulkMachineActivityResponse, SingleMachineActivityResponse, BaseSingleResponse

class MachineActivityService:
    def __init__(self, repo: MachineActivityRepository, inventory_repo: InventoryRepository, machine_repository: MachineRepository):
        self.repo = repo
        self.inventory_repo = inventory_repo
        self.machine_repo = machine_repository

    async def get_all(self, page: int, limit: int, activity_date: Optional[date], machine_id: Optional[int], inventory_id: Optional[str]) -> BulkMachineActivityResponse:
        items, total_count = await self.repo.get_all(
            page=page, limit=limit, activity_date=activity_date, machine_id=machine_id, inventory_id=inventory_id
        )
        return BulkMachineActivityResponse(
            items=items,
            item_count=total_count,
            page=page,
            limit=limit,
            total_pages=(total_count + limit - 1) // limit if total_count > 0 else 0
        )

    async def get_by_id(self, activity_id: int) -> SingleMachineActivityResponse:
        activity = await self.repo.get_by_id(activity_id)
        if not activity:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data harian mesin tidak ditemukan.")
        return SingleMachineActivityResponse(data=activity)

    async def create(self, data: MachineActivityCreateRequest) -> SingleMachineActivityResponse:
        data = data.model_dump(exclude_unset=True)
        
        # Check fk availability
        product = await self.inventory_repo.get_by_id(data.get('inventory_id'))
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produk tidak ditemukan."
            )
            
        machine = await self.machine_repo.get_by_id(data.get('machine_id'))
        if not machine:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mesin tidak ditemukan."
            )

        new_activity = await self.repo.create(data)
        
        return SingleMachineActivityResponse(message="Data harian mesin berhasil dibuat.", data=new_activity)

    async def update(self, activity_id: int, data: MachineActivityUpdateRequest) -> SingleMachineActivityResponse:
        if not await self.repo.get_by_id(activity_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data harian mesin tidak ditemukan.")
        
        update_dict = data.model_dump(exclude_unset=True)
        
        # Check fk availability
        product = await self.inventory_repo.get_by_id(update_dict.get('inventory_id'))
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produk tidak ditemukan."
            )
            
        machine = await self.machine_repo.get_by_id(update_dict.get('machine_id'))
        if not machine:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mesin tidak ditemukan."
            )
        
        updated_activity = await self.repo.update(activity_id, update_dict)
        return SingleMachineActivityResponse(message="Data harian mesin berhasil diupdate.", data=updated_activity)

    async def delete(self, activity_id: int) -> BaseSingleResponse:
        if not await self.repo.delete(activity_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data harian mesin tidak ditemukan.")
        return BaseSingleResponse(message=f"Data harian mesin berhasil dihapus.")