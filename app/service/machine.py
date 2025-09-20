from typing import Optional
from fastapi import HTTPException, status
from app.repository.machine import MachineRepository
from app.schema.request.machine import MachineCreateRequest, MachineUpdateRequest
from app.schema.response.machine import BulkMachineResponse, SingleMachineResponse, BaseSingleResponse

class MachineService:
    def __init__(self, repo: MachineRepository):
        self.repo = repo

    async def get_all(self, name: Optional[str], page: int, limit: int) -> BulkMachineResponse:
        items, total_count = await self.repo.get_all(name=name, page=page, limit=limit)
        return BulkMachineResponse(
            items=items,
            item_count=total_count,
            page=page,
            limit=limit,
            total_pages=(total_count + limit - 1) // limit if total_count > 0 else 0
        )

    async def get_by_id(self, machine_id: int) -> SingleMachineResponse:
        machine = await self.repo.get_by_id(machine_id)
        if not machine:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mesin tidak ditemukan.")
        return SingleMachineResponse(data=machine)

    async def create(self, data: MachineCreateRequest) -> SingleMachineResponse:
        new_machine = await self.repo.create(data.model_dump())
        return SingleMachineResponse(message="Mesin baru berhasil ditambahkan.", data=new_machine)

    async def update(self, machine_id: int, data: MachineUpdateRequest) -> SingleMachineResponse:
        if not await self.repo.get_by_id(machine_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mesin tidak ditemukan.")
        
        update_dict = data.model_dump(exclude_unset=True)
        updated_machine = await self.repo.update(machine_id, update_dict)
        return SingleMachineResponse(message="Data Mesin berhasil diubah.", data=updated_machine)

    async def delete(self, machine_id: int) -> BaseSingleResponse:
        if not await self.repo.delete(machine_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mesin tidak ditemukan.")
        return BaseSingleResponse(message=f"Mesin dengan id {machine_id} berhasil dihapus.")