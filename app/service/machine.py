from typing import Optional
from fastapi import HTTPException, status

from app.repository.machine import MachineRepository
from app.schema.machine.request import MachineCreateRequest, MachineUpdateRequest
from app.schema.machine.response import (
    BulkMachineResponse,
    SingleMachineResponse,
)
from app.schema.base_response import BaseSingleResponse

class MachineService:
    """Service class for machine-related business logic."""

    def __init__(self, machine_repo: MachineRepository):
        """
        Initializes the service with the machine repository.
        
        Args:
            machine_repo: The repository for machine data.
        """
        self.machine_repo = machine_repo

    async def get_all(
        self,
        name: Optional[str],
        page: int,
        limit: int,
    ) -> BulkMachineResponse:
        """
        Retrieves a paginated list of machines and formats the response.
        """
        items, total_count = await self.machine_repo.get_all(
            name=name, page=page, limit=limit
        )
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0

        return BulkMachineResponse(
            items=items,
            item_count=total_count,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )

    async def get_by_id(self, machine_id: int) -> SingleMachineResponse:
        """
        Retrieves a single machine by its ID.
        Raises an HTTPException if the machine is not found.
        """
        machine = await self.machine_repo.get_by_id(machine_id=machine_id)
        if not machine:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mesin tidak ditemukan.",
            )
        return SingleMachineResponse(data=machine)

    async def create(self, machine_create: MachineCreateRequest) -> SingleMachineResponse:
        """
        Creates a new machine after validating the name is unique.
        """
        # This check requires a `get_by_name` method in the repository.
        existing_machine = await self.machine_repo.get_by_name(name=machine_create.name)
        if existing_machine:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Mesin dengan nama '{machine_create.name}' sudah ada.",
            )

        new_machine = await self.machine_repo.create(machine_create=machine_create)
        return SingleMachineResponse(
            message="Berhasil menambahkan data mesin.", data=new_machine
        )

    async def update(
        self, machine_id: int, machine_update: MachineUpdateRequest
    ) -> SingleMachineResponse:
        """
        Updates an existing machine.
        Raises an HTTPException if the machine is not found or the new name is taken.
        """
        db_machine = await self.machine_repo.get_by_id(machine_id=machine_id)
        if not db_machine:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mesin tidak ditemukan.",
            )

        # If name is being updated, check for uniqueness
        if machine_update.name and machine_update.name != db_machine.name:
            existing_machine = await self.machine_repo.get_by_name(name=machine_update.name)
            if existing_machine:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Mesin dengan nama '{machine_update.name}' sudah ada.",
                )

        updated_machine = await self.machine_repo.update(
            db_machine=db_machine, machine_update=machine_update
        )
        return SingleMachineResponse(
            message="Berhasil mengupdate data mesin.", data=updated_machine
        )

    async def delete(self, machine_id: int) -> BaseSingleResponse:
        """
        Deletes a machine.
        Raises an HTTPException if the machine is not found.
        """
        db_machine = await self.machine_repo.get_by_id(machine_id=machine_id)
        if not db_machine:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mesin tidak ditemukan.",
            )

        await self.machine_repo.delete(db_machine=db_machine)
        return BaseSingleResponse(
            message=f"Berhasil menghapus data mesin dengan id {machine_id}."
        )