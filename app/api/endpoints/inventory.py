from typing import Optional
from fastapi import APIRouter, Depends, status, Query

# --- Dependency Imports ---
from app.service.inventory import InventoryService
from app.di.core import get_inventory_service

# --- Pydantic Schema & Model Imports ---
from app.schema.inventory.request import InventoryCreateRequest, InventoryUpdateRequest
from app.schema.inventory.response import (
    BulkInventoryResponse,
    SingleInventoryResponse,
)
from app.schema.base_response import BaseSingleResponse
from app.model.inventory import InventoryType
from app.di.deps import get_current_user

# --- Router Initialization ---
router = APIRouter(
    prefix="/inventory",
    tags=["Inventories"],
    dependencies=[Depends(get_current_user)]
)

# --- API Endpoints ---

@router.post("", status_code=status.HTTP_201_CREATED, response_model=SingleInventoryResponse)
async def create_inventory(
    request_data: InventoryCreateRequest,
    service: InventoryService = Depends(get_inventory_service),
):
    """
    ### Create a new Inventory item.

    This endpoint registers a new item in the inventory, which can be a raw material
    (e.g., THREAD) or a finished product (e.g., FABRIC).

    - **id**: A unique identifier for the item. The service will raise an error if this ID is already in use.
    - **name**: The display name of the item.
    - **type**: The type of item (`fabric` or `thread`).
    """
    return await service.create(inventory_create=request_data)

@router.get("", response_model=BulkInventoryResponse)
async def get_all_inventories(
    page: int = Query(1, ge=1, description="Page number to retrieve"),
    limit: int = Query(10, ge=1, le=9999, description="Number of items per page"),
    name: Optional[str] = Query(None, description="Filter by item name. Case-insensitive search."),
    id: Optional[str] = Query(None, description="Filter by item ID. Case-insensitive search."),
    type: Optional[InventoryType] = Query(None, description="Filter by item type ('fabric' or 'thread')."),
    service: InventoryService = Depends(get_inventory_service),
):
    """
    ### Retrieve all Inventory items.

    Provides a paginated and filterable list of all items in the inventory.
    """
    return await service.get_all(
        page=page,
        limit=limit,
        name=name,
        id=id,
        type=type,
    )

@router.get("/{inventory_id}", response_model=SingleInventoryResponse)
async def get_inventory_by_id(
    inventory_id: str,
    service: InventoryService = Depends(get_inventory_service),
):
    """
    ### Get a single Inventory item by ID.

    Retrieve the details and current stock levels of a specific inventory item
    using its unique ID.
    """
    return await service.get_by_id(inventory_id=inventory_id)

@router.put("/{inventory_id}", response_model=SingleInventoryResponse)
async def update_inventory(
    inventory_id: str,
    request_data: InventoryUpdateRequest,
    service: InventoryService = Depends(get_inventory_service),
):
    """
    ### Update an Inventory item.

    Modify the details of an existing inventory item, such as its name or stock levels.
    Note: Manually updating stock levels via this endpoint is generally discouraged.
    Stock should be managed automatically via Sales and Purchase transactions.
    """
    return await service.update(inventory_id=inventory_id, inventory_update=request_data)

@router.delete("/{inventory_id}", response_model=BaseSingleResponse)
async def delete_inventory(
    inventory_id: str,
    service: InventoryService = Depends(get_inventory_service),
):
    """
    ### Delete an Inventory item.

    Permanently remove an inventory item from the database.
    **Warning**: This can fail if the item is referenced in existing transactions or formulas.
    """
    return await service.delete(inventory_id=inventory_id)