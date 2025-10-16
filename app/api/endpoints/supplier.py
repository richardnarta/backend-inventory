from typing import Optional
from fastapi import APIRouter, Depends, status, Query

# --- Dependency Imports ---
from app.service.supplier import SupplierService
from app.di.core import get_supplier_service

# --- Pydantic Schema Imports ---
from app.schema.supplier.request import SupplierCreateRequest, SupplierUpdateRequest
from app.schema.supplier.response import (
    BulkSupplierResponse,
    SingleSupplierResponse,
)
from app.schema.base_response import BaseSingleResponse
from app.di.deps import get_current_user

# --- Router Initialization ---
router = APIRouter(
    prefix="/supplier",
    tags=["Suppliers"],
    dependencies=[Depends(get_current_user)]
)

# --- API Endpoints ---

@router.post("", status_code=status.HTTP_201_CREATED, response_model=SingleSupplierResponse)
async def create_supplier(
    request_data: SupplierCreateRequest,
    service: SupplierService = Depends(get_supplier_service),
):
    """
    ### Create a new Supplier.

    This endpoint registers a new supplier in the system.
    - **name**: The name of the supplier (required).
    - **phone_num**: Contact phone number (optional).
    - **address**: Physical address (optional).
    - **note**: Any additional notes about the supplier (optional).
    """
    return await service.create(supplier_create=request_data)

@router.get("", response_model=BulkSupplierResponse)
async def get_all_suppliers(
    name: Optional[str] = Query(None, description="Filter by supplier name. Case-insensitive search."),
    page: int = Query(1, ge=1, description="Page number to retrieve"),
    limit: int = Query(10, ge=1, le=9999, description="Number of items per page"),
    service: SupplierService = Depends(get_supplier_service),
):
    """
    ### Retrieve all Suppliers.

    Provides a paginated and filterable list of all suppliers.
    """
    return await service.get_all(name=name, page=page, limit=limit)

@router.get("/{supplier_id}", response_model=SingleSupplierResponse)
async def get_supplier_by_id(
    supplier_id: int,
    service: SupplierService = Depends(get_supplier_service),
):
    """
    ### Get a single Supplier by ID.

    Retrieve the details of a specific supplier using their unique ID.
    """
    return await service.get_by_id(supplier_id=supplier_id)

@router.put("/{supplier_id}", response_model=SingleSupplierResponse)
async def update_supplier(
    supplier_id: int,
    request_data: SupplierUpdateRequest,
    service: SupplierService = Depends(get_supplier_service),
):
    """
    ### Update a Supplier's details.

    Modify the details of an existing supplier by their ID.
    Fields that are not provided will remain unchanged.
    """
    return await service.update(supplier_id=supplier_id, supplier_update=request_data)

@router.delete("/{supplier_id}", response_model=BaseSingleResponse)
async def delete_supplier(
    supplier_id: int,
    service: SupplierService = Depends(get_supplier_service),
):
    """
    ### Delete a Supplier.

    Permanently remove a supplier from the database by their unique ID.
    """
    return await service.delete(supplier_id=supplier_id)