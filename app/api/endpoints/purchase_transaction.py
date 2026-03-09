from typing import Optional, List
from datetime import date
from fastapi import APIRouter, Depends, status, Query
from pydantic import BaseModel

# --- Dependency Imports ---
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
from app.di.deps import get_current_user, require_write_access

# --- Request Body Schema for Bulk Delete ---
class BulkDeleteIntRequest(BaseModel):
    ids: Optional[List[int]] = None
    delete_all: bool = False


# --- Router Initialization ---
router = APIRouter(
    prefix="/purchase-transaction",
    tags=["Purchase Transactions"],
    dependencies=[Depends(get_current_user)]
)

# --- API Endpoints ---

@router.post("", status_code=status.HTTP_201_CREATED, response_model=SinglePurchaseTransactionResponse, dependencies=[Depends(require_write_access)])
async def create_purchase_transaction(
    request_data: PurchaseTransactionCreateRequest,
    service: PurchaseTransactionService = Depends(get_purchase_transaction_service),
):
    """
    ### Create a new Purchase Transaction with Multiple Items.

    This endpoint creates a purchase transaction that can contain multiple inventory items.
    Automatically updates inventory stock for all items (+quantity for each item).
    """
    return await service.create(pt_create=request_data)

@router.get("", response_model=BulkPurchaseTransactionResponse)
async def get_all_purchase_transactions(
    page: int = Query(1, ge=1, description="Page number to retrieve"),
    limit: int = Query(10, ge=1, le=99999, description="Number of items per page"),
    supplier_id: Optional[int] = Query(None, description="Filter by Supplier ID"),
    inventory_id: Optional[str] = Query(None, description="Filter by Inventory Item kode_barang"),
    start_date: Optional[date] = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Filter by end date (YYYY-MM-DD)"),
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

@router.put("/{pt_id}", response_model=SinglePurchaseTransactionResponse, dependencies=[Depends(require_write_access)])
async def update_purchase_transaction(
    pt_id: int,
    request_data: PurchaseTransactionUpdateRequest,
    service: PurchaseTransactionService = Depends(get_purchase_transaction_service),
):
    """
    ### Update a Purchase Transaction.

    Updates transaction header and/or items. Automatically adjusts inventory stock:
    - Rollbacks old items stock
    - Applies new items stock
    """
    return await service.update(pt_id=pt_id, pt_update=request_data)

@router.delete("/{pt_id}", response_model=BaseSingleResponse, dependencies=[Depends(require_write_access)])
async def delete_purchase_transaction(
    pt_id: int,
    service: PurchaseTransactionService = Depends(get_purchase_transaction_service),
):
    """
    ### Delete a Purchase Transaction.

    Permanently deletes purchase transaction and all items.
    Automatically rollbacks inventory stock for all items.
    """
    return await service.delete(pt_id=pt_id)

@router.delete("/bulk/delete", response_model=BaseSingleResponse, dependencies=[Depends(require_write_access)])
async def bulk_delete_purchase_transactions(
    request_data: BulkDeleteIntRequest,
    service: PurchaseTransactionService = Depends(get_purchase_transaction_service),
):
    """
    ### Bulk Delete Purchase Transactions.

    Delete multiple purchase transactions at once. Stock rollback is applied for each.
    - **delete_all**: If true, deletes ALL purchase transactions.
    - **ids**: List of transaction IDs to delete.
    """
    return await service.bulk_delete(ids=request_data.ids, delete_all=request_data.delete_all)