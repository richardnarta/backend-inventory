from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, status, Query

# --- Dependency Imports ---
from app.service.knitting_process import KnittingProcessService
from app.di.core import get_knitting_process_service

# --- Pydantic Schema Imports ---
from app.schema.knitting_process.request import (
    KnittingProcessCreateRequest,
    KnittingProcessUpdateRequest,
)
from app.schema.knitting_process.response import (
    BulkKnittingProcessResponse,
    SingleKnittingProcessResponse,
)
from app.schema.base_response import BaseSingleResponse

# --- Router Initialization ---
router = APIRouter(
    prefix="/knitting-process",
    tags=["Knitting Processes"],
)

# --- API Endpoints ---

@router.post("", status_code=status.HTTP_201_CREATED, response_model=SingleKnittingProcessResponse)
async def create_knitting_process(
    request_data: KnittingProcessCreateRequest,
    service: KnittingProcessService = Depends(get_knitting_process_service),
):
    """
    ### Start a new Knitting Process.

    This endpoint creates a new knitting production record.

    - **knit_formula_id**: The formula to be used for production.
    - **operator_id**: The operator responsible for the process.
    - **machine_id**: The machine used for the process.
    - **weight_kg**: The target weight of the final product to be produced.

    **Business Logic**:
    1.  Validates that the formula, operator, and machine exist.
    2.  Calculates the required weight of each raw material (thread) based on the formula.
    3.  Checks for sufficient stock of all required materials.
    4.  **Subtracts** the required material weights from the inventory.
    """
    return await service.create(kp_create=request_data)

@router.get("", response_model=BulkKnittingProcessResponse)
async def get_all_knitting_processes(
    page: int = Query(1, ge=1, description="Page number to retrieve"),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page"),
    knit_formula_id: Optional[int] = Query(None, description="Filter by Knit Formula ID"),
    start_date: Optional[date] = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Filter by end date (YYYY-MM-DD)"),
    service: KnittingProcessService = Depends(get_knitting_process_service),
):
    """
    ### Retrieve all Knitting Processes.

    Provides a paginated and filterable list of all knitting production records.
    """
    return await service.get_all(
        page=page,
        limit=limit,
        knit_formula_id=knit_formula_id,
        start_date=start_date,
        end_date=end_date,
    )

@router.get("/{kp_id}", response_model=SingleKnittingProcessResponse)
async def get_knitting_process_by_id(
    kp_id: int,
    service: KnittingProcessService = Depends(get_knitting_process_service),
):
    """
    ### Get a single Knitting Process by ID.

    Retrieve the details of a specific knitting process using its unique ID.
    """
    return await service.get_by_id(kp_id=kp_id)

@router.put("/{kp_id}", response_model=SingleKnittingProcessResponse)
async def update_knitting_process(
    kp_id: int,
    request_data: KnittingProcessUpdateRequest,
    service: KnittingProcessService = Depends(get_knitting_process_service),
):
    """
    ### Update a Knitting Process.

    Modify an existing knitting process, typically to mark it as complete.

    **Business Logic**:
    - If `knit_status` is updated to `True`, the process is marked as complete.
    - The final product's weight (`weight_kg`) is **added** to its corresponding inventory item.
    - A process that is already complete cannot be updated.
    """
    return await service.update(kp_id=kp_id, kp_update=request_data)

@router.delete("/{kp_id}", response_model=BaseSingleResponse)
async def delete_knitting_process(
    kp_id: int,
    service: KnittingProcessService = Depends(get_knitting_process_service),
):
    """
    ### Delete a Knitting Process.

    Permanently remove a knitting process record.

    **Business Logic**: This action performs a **full rollback** of all inventory changes.
    1.  The consumed raw materials are **added back** to their respective inventory stocks.
    2.  If the process was already completed, the final product that was created is **subtracted** from its inventory stock.
    """
    return await service.delete(kp_id=kp_id)