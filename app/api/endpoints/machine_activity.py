from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, status, Query
from app.service.machine_activity import MachineActivityService
from app.di.core import get_machine_activity_service
from app.schema.request.machine_activity import MachineActivityCreateRequest, MachineActivityUpdateRequest
from app.schema.response.machine_activity import BulkMachineActivityResponse, SingleMachineActivityResponse, BaseSingleResponse

router = APIRouter()

@router.post("", status_code=status.HTTP_201_CREATED, response_model=SingleMachineActivityResponse)
async def create_activity(req: MachineActivityCreateRequest, service: MachineActivityService = Depends(get_machine_activity_service)):
    return await service.create(req)

@router.get("", response_model=BulkMachineActivityResponse)
async def get_all_activities(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=9999),
    date: Optional[date] = Query(None, description="Filter by activity date"),
    machine_id: Optional[int] = Query(None, description="Filter by machine ID"),
    inventory_id: Optional[str] = Query(None, description="Filter by product/inventory ID"),
    service: MachineActivityService = Depends(get_machine_activity_service)
):
    return await service.get_all(page=page, limit=limit, activity_date=date, machine_id=machine_id, inventory_id=inventory_id)

@router.get("/{activity_id}", response_model=SingleMachineActivityResponse)
async def get_activity_by_id(activity_id: int, service: MachineActivityService = Depends(get_machine_activity_service)):
    return await service.get_by_id(activity_id)

@router.put("/{activity_id}", response_model=SingleMachineActivityResponse)
async def update_activity(activity_id: int, req: MachineActivityUpdateRequest, service: MachineActivityService = Depends(get_machine_activity_service)):
    return await service.update(activity_id, req)

@router.delete("/{activity_id}", response_model=BaseSingleResponse)
async def delete_activity(activity_id: int, service: MachineActivityService = Depends(get_machine_activity_service)):
    return await service.delete(activity_id)