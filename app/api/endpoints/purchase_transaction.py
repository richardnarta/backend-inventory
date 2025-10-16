from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, status, Query

# --- Dependency Imports ---
from app.model.inventory import InventoryType
from app.service.purchase_transaction import PurchaseTransactionService
from app.di.core import get_purchase_transaction_service

# --- Pydantic Schema Imports ---
from app.schema.purchase_transaction.request import (
    PurchaseTransactionCreateRequest,
    PurchaseTransactionUpdateRequest,
)
from app.schema.purchase_transaction.response import (
    BulkPurchaseTransactionResponse,
    SinglePurchaseTransactionResponse,
)
from app.schema.base_response import BaseSingleResponse
from app.di.deps import get_current_user

# --- Router Initialization ---
router = APIRouter(
    prefix="/purchase-transaction",
    tags=["Purchase Transactions"],
    dependencies=[Depends(get_current_user)]
)

# --- API Endpoints ---

@router.post("", status_code=status.HTTP_201_CREATED, response_model=SinglePurchaseTransactionResponse)
async def create_purchase_transaction(
    request_data: PurchaseTransactionCreateRequest,
    service: PurchaseTransactionService = Depends(get_purchase_transaction_service),
):
    """
    ### Create a new Purchase Transaction.

    This endpoint records a new purchase of inventory items from a supplier.

    **Business Logic**:
    - Validates that the `supplier_id` and `inventory_id` exist.
    - Automatically **increases** the stock levels (`roll_count`, `weight_kg`, `bale_count`)
      of the specified inventory item.
    """
    return await service.create(pt_create=request_data)

@router.get("", response_model=BulkPurchaseTransactionResponse)
async def get_all_purchase_transactions(
    page: int = Query(1, ge=1, description="Page number to retrieve"),
    limit: int = Query(10, ge=1, le=99999, description="Number of items per page"),
    supplier_id: Optional[int] = Query(None, description="Filter by Supplier ID"),
    inventory_id: Optional[str] = Query(None, description="Filter by Inventory Item ID"),
    start_date: Optional[date] = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Filter by end date (YYYY-MM-DD)"),
    type: Optional[InventoryType] = Query(None, description="Filter by inventory type ('fabric' or 'thread')"),
    service: PurchaseTransactionService = Depends(get_purchase_transaction_service),
):
    """
    ### Retrieve all Purchase Transactions.

    Provides a paginated and filterable list of all purchase transaction records.
    """
    return await service.get_all(
        page=page,
        limit=limit,
        supplier_id=supplier_id,
        inventory_id=inventory_id,
        start_date=start_date,
        end_date=end_date,
        inventory_type=type,
    )

@router.get("/{pt_id}", response_model=SinglePurchaseTransactionResponse)
async def get_purchase_transaction_by_id(
    pt_id: int,
    service: PurchaseTransactionService = Depends(get_purchase_transaction_service),
):
    """
    ### Get a single Purchase Transaction by ID.

    Retrieve the details of a specific purchase transaction using its unique ID.
    """
    return await service.get_by_id(pt_id=pt_id)

@router.put("/{pt_id}", response_model=SinglePurchaseTransactionResponse)
async def update_purchase_transaction(
    pt_id: int,
    request_data: PurchaseTransactionUpdateRequest,
    service: PurchaseTransactionService = Depends(get_purchase_transaction_service),
):
    """
    ### Update a Purchase Transaction.

    Modify an existing purchase transaction.

    **Business Logic**:
    - Automatically **adjusts** the inventory stock based on the difference
      between the old and new quantities. For example, changing `weight_kg` from
      100 to 120 will add 20 to the item's stock.
    """
    return await service.update(pt_id=pt_id, pt_update=request_data)

@router.delete("/{pt_id}", response_model=BaseSingleResponse)
async def delete_purchase_transaction(
    pt_id: int,
    service: PurchaseTransactionService = Depends(get_purchase_transaction_service),
):
    """
    ### Delete a Purchase Transaction.

    Permanently remove a purchase transaction record.

    **Business Logic**:
    - This action **reverses** the initial stock change by **subtracting** the
      transaction's quantities from the corresponding inventory item.
    """
    return await service.delete(pt_id=pt_id)