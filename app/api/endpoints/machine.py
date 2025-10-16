from typing import Optional
from fastapi import APIRouter, Depends, status, Query

# --- Dependency Imports ---
from app.service.machine import MachineService
from app.di.core import get_machine_service

# --- Pydantic Schema Imports ---
from app.schema.machine.request import MachineCreateRequest, MachineUpdateRequest
from app.schema.machine.response import (
    BulkMachineResponse,
    SingleMachineResponse,
)
from app.schema.base_response import BaseSingleResponse
from app.di.deps import get_current_user

# --- Router Initialization ---
router = APIRouter(
    prefix="/machine",
    tags=["Machines"],
    dependencies=[Depends(get_current_user)]
)

# --- API Endpoints ---

@router.post("", status_code=status.HTTP_201_CREATED, response_model=SingleMachineResponse)
async def create_machine(
    request_data: MachineCreateRequest,
    service: MachineService = Depends(get_machine_service),
):
    """
    ### Create a new Machine.

    This endpoint registers a new machine in the system.
    
    - **name**: The name of the machine. **Must be unique.**
    """
    return await service.create(machine_create=request_data)

@router.get("", response_model=BulkMachineResponse)
async def get_all_machines(
    name: Optional[str] = Query(None, description="Filter by machine name. Case-insensitive search."),
    page: int = Query(1, ge=1, description="Page number to retrieve"),
    limit: int = Query(10, ge=1, le=9999, description="Number of items per page"),
    service: MachineService = Depends(get_machine_service),
):
    """
    ### Retrieve all Machines.

    Provides a paginated and filterable list of all machines.
    """
    return await service.get_all(name=name, page=page, limit=limit)

@router.get("/{machine_id}", response_model=SingleMachineResponse)
async def get_machine_by_id(
    machine_id: int,
    service: MachineService = Depends(get_machine_service),
):
    """
    ### Get a single Machine by ID.

    Retrieve the details of a specific machine using its unique ID.
    """
    return await service.get_by_id(machine_id=machine_id)

@router.put("/{machine_id}", response_model=SingleMachineResponse)
async def update_machine(
    machine_id: int,
    request_data: MachineUpdateRequest,
    service: MachineService = Depends(get_machine_service),
):
    """
    ### Update a Machine's details.

    Modify the name of an existing machine.
    
    - **name**: The new name for the machine. **Must be unique.**
    """
    return await service.update(machine_id=machine_id, machine_update=request_data)

@router.delete("/{machine_id}", response_model=BaseSingleResponse)
async def delete_machine(
    machine_id: int,
    service: MachineService = Depends(get_machine_service),
):
    """
    ### Delete a Machine.

    Permanently remove a machine from the database by its unique ID.
    """
    return await service.delete(machine_id=machine_id)