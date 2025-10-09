from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, status, Query

# --- Dependency Imports ---
from app.service.dyeing_process import DyeingProcessService
from app.di.core import get_dyeing_process_service

# --- Pydantic Schema Imports ---
from app.schema.dyeing_process.request import (
    DyeingProcessCreateRequest,
    DyeingProcessUpdateRequest,
)
from app.schema.dyeing_process.response import (
    BulkDyeingProcessResponse,
    SingleDyeingProcessResponse,
)
from app.schema.base_response import BaseSingleResponse

# --- Router Initialization ---
router = APIRouter(
    prefix="/dyeing-process",
    tags=["Dyeing Processes"],
)

# --- API Endpoints ---

@router.post("", status_code=status.HTTP_201_CREATED, response_model=SingleDyeingProcessResponse)
async def create_dyeing_process(
    request_data: DyeingProcessCreateRequest,
    service: DyeingProcessService = Depends(get_dyeing_process_service),
):
    """
    ### Start a new Dyeing Process.

    This endpoint creates a new dyeing process record.
    - **product_id**: The ID of the inventory item to be dyed.
    - **dyeing_weight**: The weight of the product to be used.

    **Business Logic**: Upon creation, the `dyeing_weight` is **subtracted** from the
    product's inventory stock. The `start_date` is set automatically.
    """
    return await service.create(dp_create=request_data)

@router.get("", response_model=BulkDyeingProcessResponse)
async def get_all_dyeing_processes(
    page: int = Query(1, ge=1, description="Page number to retrieve"),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page"),
    start_date: Optional[date] = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Filter by end date (YYYY-MM-DD)"),
    dyeing_status: Optional[bool] = Query(None, description="Filter by status (True=complete, False=in-progress)"),
    service: DyeingProcessService = Depends(get_dyeing_process_service),
):
    """
    ### Retrieve all Dyeing Processes.

    Provides a paginated and filterable list of all dyeing process records.
    """
    return await service.get_all(
        page=page,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
        dyeing_status=dyeing_status,
    )

@router.get("/{dp_id}", response_model=SingleDyeingProcessResponse)
async def get_dyeing_process_by_id(
    dp_id: int,
    service: DyeingProcessService = Depends(get_dyeing_process_service),
):
    """
    ### Get a single Dyeing Process by ID.

    Retrieve the details of a specific dyeing process using its unique ID.
    """
    return await service.get_by_id(dp_id=dp_id)

@router.put("/{dp_id}", response_model=SingleDyeingProcessResponse)
async def update_dyeing_process(
    dp_id: int,
    request_data: DyeingProcessUpdateRequest,
    service: DyeingProcessService = Depends(get_dyeing_process_service),
):
    """
    ### Update a Dyeing Process.

    Modify an existing dyeing process.
    
    **Business Logic**: If `dyeing_status` is updated to `True`, the process is
    marked as complete.
    - You **must** provide `end_date`, `dyeing_final_weight`, and `dyeing_overhead_cost`.
    - The `dyeing_final_weight` will be **added** to the product's inventory stock.
    - A process that is already complete cannot be updated.
    """
    return await service.update(dp_id=dp_id, dp_update=request_data)

@router.delete("/{dp_id}", response_model=BaseSingleResponse)
async def delete_dyeing_process(
    dp_id: int,
    service: DyeingProcessService = Depends(get_dyeing_process_service),
):
    """
    ### Delete a Dyeing Process.

    Permanently remove a dyeing process record.

    **Business Logic**: This action **rolls back** all inventory changes.
    - The initial `dyeing_weight` is added back to the product's stock.
    - If the process was completed, the `dyeing_final_weight` is subtracted.
    """
    return await service.delete(dp_id=dp_id)