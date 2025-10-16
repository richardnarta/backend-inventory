from typing import Optional
from fastapi import APIRouter, Depends, status, Query

# --- Dependency Imports ---
from app.service.operator import OperatorService
from app.di.core import get_operator_service

# --- Pydantic Schema Imports ---
from app.schema.operator.request import OperatorCreateRequest, OperatorUpdateRequest
from app.schema.operator.response import (
    BulkOperatorResponse,
    SingleOperatorResponse,
)
from app.schema.base_response import BaseSingleResponse
from app.di.deps import get_current_user

# --- Router Initialization ---
router = APIRouter(
    prefix="/operator",
    tags=["Operators"],
    dependencies=[Depends(get_current_user)]
)

# --- API Endpoints ---

@router.post("", status_code=status.HTTP_201_CREATED, response_model=SingleOperatorResponse)
async def create_operator(
    request_data: OperatorCreateRequest,
    service: OperatorService = Depends(get_operator_service),
):
    """
    ### Create a new Operator.

    This endpoint registers a new machine operator in the system.
    
    - **name**: The name of the operator (required).
    - **phone_num**: Contact phone number (optional).
    """
    return await service.create(operator_create=request_data)

@router.get("", response_model=BulkOperatorResponse)
async def get_all_operators(
    name: Optional[str] = Query(None, description="Filter by operator name. Case-insensitive search."),
    page: int = Query(1, ge=1, description="Page number to retrieve"),
    limit: int = Query(10, ge=1, le=9999, description="Number of items per page"),
    service: OperatorService = Depends(get_operator_service),
):
    """
    ### Retrieve all Operators.

    Provides a paginated and filterable list of all machine operators.
    """
    return await service.get_all(name=name, page=page, limit=limit)

@router.get("/{operator_id}", response_model=SingleOperatorResponse)
async def get_operator_by_id(
    operator_id: int,
    service: OperatorService = Depends(get_operator_service),
):
    """
    ### Get a single Operator by ID.

    Retrieve the details of a specific operator using their unique ID.
    """
    return await service.get_by_id(operator_id=operator_id)

@router.put("/{operator_id}", response_model=SingleOperatorResponse)
async def update_operator(
    operator_id: int,
    request_data: OperatorUpdateRequest,
    service: OperatorService = Depends(get_operator_service),
):
    """
    ### Update an Operator's details.

    Modify the details of an existing operator by their ID.
    """
    return await service.update(operator_id=operator_id, operator_update=request_data)

@router.delete("/{operator_id}", response_model=BaseSingleResponse)
async def delete_operator(
    operator_id: int,
    service: OperatorService = Depends(get_operator_service),
):
    """
    ### Delete an Operator.

    Permanently remove an operator from the database by their unique ID.
    """
    return await service.delete(operator_id=operator_id)