from typing import Optional
from fastapi import APIRouter, Depends, status, Query
from app.service.machine import MachineService
from app.di.core import get_machine_service
from app.schema.request.machine import MachineCreateRequest, MachineUpdateRequest
from app.schema.response.machine import BulkMachineResponse, SingleMachineResponse, BaseSingleResponse

router = APIRouter()

@router.post("", status_code=status.HTTP_201_CREATED, response_model=SingleMachineResponse)
async def create_machine(req: MachineCreateRequest, service: MachineService = Depends(get_machine_service)):
    return await service.create(req)

@router.get("", response_model=BulkMachineResponse)
async def get_all_machines(
    name: Optional[str] = Query(None, description="Filter by name"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=9999),
    service: MachineService = Depends(get_machine_service)
):
    return await service.get_all(name=name, page=page, limit=limit)

@router.get("/{machine_id}", response_model=SingleMachineResponse)
async def get_machine_by_id(machine_id: int, service: MachineService = Depends(get_machine_service)):
    return await service.get_by_id(machine_id)

@router.put("/{machine_id}", response_model=SingleMachineResponse)
async def update_machine(machine_id: int, req: MachineUpdateRequest, service: MachineService = Depends(get_machine_service)):
    return await service.update(machine_id, req)

@router.delete("/{machine_id}", response_model=BaseSingleResponse)
async def delete_machine(machine_id: int, service: MachineService = Depends(get_machine_service)):
    return await service.delete(machine_id)