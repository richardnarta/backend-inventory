from typing import Optional
from fastapi import APIRouter, Depends, status, Query

# --- Dependency Imports ---
from app.service.inventory import InventoryService
from app.di.core import get_inventory_service

# --- Pydantic Schema Imports ---
from app.schema.request.inventory import InventoryCreateRequest, InventoryUpdateRequest
from app.schema.response.inventory import (
    BulkInventoryResponse, 
    SingleInventoryResponse,
    BaseSingleResponse
)

# --- Router Initialization ---
router = APIRouter()


# --- API Endpoints ---

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=SingleInventoryResponse)
async def create_inventory_item(
    request_data: InventoryCreateRequest,
    service: InventoryService = Depends(get_inventory_service)
):
    """
    Create a new inventory item.
    """
    return await service.create(request_data)

@router.get("/", response_model=BulkInventoryResponse)
async def get_all_inventory_items(
    name: Optional[str] = Query(None, description="Filter by item name (case-insensitive)"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    service: InventoryService = Depends(get_inventory_service)
):
    """
    Retrieve a paginated list of all inventory items.
    """
    return await service.get_all(name=name, page=page, limit=limit)

@router.get("/{item_id}", response_model=SingleInventoryResponse)
async def get_inventory_item_by_id(
    item_id: str,
    service: InventoryService = Depends(get_inventory_service)
):
    """
    Retrieve a single inventory item by its ID.
    """
    return await service.get_by_id(item_id)

@router.put("/{item_id}", response_model=SingleInventoryResponse)
async def update_inventory_item(
    item_id: str,
    request_data: InventoryUpdateRequest,
    service: InventoryService = Depends(get_inventory_service)
):
    """
    Update an existing inventory item.
    """
    return await service.update(item_id, request_data)

@router.delete("/{item_id}", response_model=BaseSingleResponse)
async def delete_inventory_item(
    item_id: str,
    service: InventoryService = Depends(get_inventory_service)
):
    """
    Delete an inventory item by its ID.
    """
    return await service.delete(item_id)
