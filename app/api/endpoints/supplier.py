from typing import Optional
from fastapi import APIRouter, Depends, status, Query

# --- Dependency Imports ---
from app.service.supplier import SupplierService
from app.di.core import get_supplier_service

# --- Pydantic Schema Imports ---
from app.schema.request.supplier import SupplierCreateRequest, SupplierUpdateRequest
from app.schema.response.supplier import (
    BulkSupplierResponse, 
    SingleSupplierResponse,
    BaseSingleResponse
)

# --- Router Initialization ---
router = APIRouter()


# --- API Endpoints ---

@router.post("", status_code=status.HTTP_201_CREATED, response_model=SingleSupplierResponse)
async def create_supplier(
    request_data: SupplierCreateRequest,
    service: SupplierService = Depends(get_supplier_service)
):
    """
    Create a new supplier.
    """
    return await service.create(request_data)

@router.get("", response_model=BulkSupplierResponse)
async def get_all_suppliers(
    name: Optional[str] = Query(None, description="Filter by supplier name (case-insensitive)"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=9999, description="Items per page"),
    service: SupplierService = Depends(get_supplier_service)
):
    """
    Retrieve a paginated list of all suppliers.
    """
    return await service.get_all(name=name, page=page, limit=limit)

@router.get("/{supplier_id}", response_model=SingleSupplierResponse)
async def get_supplier_by_id(
    supplier_id: int,
    service: SupplierService = Depends(get_supplier_service)
):
    """
    Retrieve a single supplier by their ID.
    """
    return await service.get_by_id(supplier_id)

@router.put("/{supplier_id}", response_model=SingleSupplierResponse)
async def update_supplier(
    supplier_id: int,
    request_data: SupplierUpdateRequest,
    service: SupplierService = Depends(get_supplier_service)
):
    """
    Update an existing supplier.
    """
    return await service.update(supplier_id, request_data)

@router.delete("/{supplier_id}", response_model=BaseSingleResponse)
async def delete_supplier(
    supplier_id: int,
    service: SupplierService = Depends(get_supplier_service)
):
    """
    Delete a supplier by their ID.
    """
    return await service.delete(supplier_id)
