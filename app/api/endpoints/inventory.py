from typing import Optional
from fastapi import APIRouter, Depends, status, Query, UploadFile, File

# --- Dependency Imports ---
from app.service.inventory import InventoryService
from app.di.core import get_inventory_service

# --- Pydantic Schema & Model Imports ---
from app.schema.inventory.request import InventoryCreateRequest, InventoryUpdateRequest
from app.schema.inventory.response import (
    BulkInventoryResponse,
    SingleInventoryResponse,
)
from app.schema.inventory.batch_response import BatchUploadResponse
from app.schema.base_response import BaseSingleResponse
from app.di.deps import get_current_user
from app.utils.excel_processor import process_excel_file
from app.utils.excel_exporter import generate_inventory_export

# --- Router Initialization ---
router = APIRouter(
    prefix="/inventory",
    tags=["Inventories"],
    dependencies=[Depends(get_current_user)]
)

# --- API Endpoints ---

@router.get("/export-excel")
async def export_inventory_excel(
    service: InventoryService = Depends(get_inventory_service),
):
    """
    ### Export all inventory items to Excel file.
    
    Downloads an Excel file with all inventory data in the same format as import template.
    Useful for backup or editing inventory in bulk.
    
    **Format:**
    - Row 1-2: Headers
    - Row 3+: Data
    - Columns: A=Kode, C=Nama, F=Satuan, G=Modal, H=Eceran, I=Qty, P=Keterangan
    """
    # Get all inventory items (no pagination)
    result = await service.get_all(
        nama_barang=None,
        kode_barang=None,
        quantity_unit=None,
        page=1,
        limit=999999  # Get all items
    )
    
    # Convert response items to Inventory models for exporter
    from app.model.inventory import Inventory
    inventories = [Inventory(**item.model_dump()) for item in result.items]
    
    return generate_inventory_export(inventories)

@router.post("/batch-upload", status_code=status.HTTP_201_CREATED, response_model=BatchUploadResponse)
async def batch_upload_inventory(
    file: UploadFile = File(..., description="Excel file (.xlsx or .xls) containing inventory data"),
    service: InventoryService = Depends(get_inventory_service),
):
    """
    ### Batch upload inventory items from Excel file.
    
    Upload an Excel file to create multiple inventory items at once.
    
    **Excel Format Requirements:**
    - Row 1-2: Headers (will be skipped)
    - Row 3+: Data rows
    - Column A: Kode Barang (Item Code)
    - Column C: Nama Barang (Item Name)
    - Column F: Satuan (Unit) - will be mapped automatically
    - Column G: Harga Modal (Cost Price)
    - Column H: Harga Jual Eceran (Retail Price)
    - Column I: Qty (Quantity)
    - Column P: Keterangan (Additional Note)
    
    **Unit Mapping:**
    - DUS/dus → Dus
    - BTG/btg → Batang
    - BAL/bal → Bal
    - BH/PCS/pcs/bh → Pcs
    - lbr/LBR → Lembar
    - ls/LS → Lusin
    - m/M → Meter
    - pak/PAK → Pak
    - ons/ONS → Ons
    - sak/SAK → Sak
    - kg/KG → Kilogram
    - kotak/KOTAK → Kotak
    
    **Behavior:**
    - Rows with unmapped units will be skipped
    - Duplicate kode_barang will be skipped
    - Empty rows will be skipped
    """
    # Process Excel file
    valid_items, skipped_count, new_units = await process_excel_file(file)
    
    # Batch upload to database
    upload_result = await service.batch_upload_from_excel(valid_items)
    
    total_processed = len(valid_items) + skipped_count
    
    return BatchUploadResponse(
        message=f"Berhasil memproses {total_processed} baris data.",
        total_rows_processed=total_processed,
        successful_imports=upload_result["successful_count"],
        skipped_rows=skipped_count,
        new_units_detected=new_units,
        duplicate_skipped=upload_result["duplicate_count"]
    )

@router.post("", status_code=status.HTTP_201_CREATED, response_model=SingleInventoryResponse)
async def create_inventory(
    request_data: InventoryCreateRequest,
    service: InventoryService = Depends(get_inventory_service),
):
    """
    ### Create a new Inventory item.

    This endpoint registers a new item in the inventory system.

    - **kode_barang**: A unique identifier for the item (will be converted to uppercase).
    - **nama_barang**: The display name of the item.
    - **quantity**: Current stock quantity.
    - **quantity_unit**: Unit of measurement (buah, lusin, kodi, dus, bal).
    - **harga_modal**: Cost price / purchase price.
    - **harga_jual_eceran**: Retail selling price.
    - **harga_jual_grosir**: Wholesale selling price.
    """
    return await service.create(inventory_create=request_data)

@router.get("", response_model=BulkInventoryResponse)
async def get_all_inventories(
    page: int = Query(1, ge=1, description="Page number to retrieve"),
    limit: int = Query(10, ge=1, le=9999, description="Number of items per page"),
    nama_barang: Optional[str] = Query(None, description="Filter by item name. Case-insensitive search."),
    kode_barang: Optional[str] = Query(None, description="Filter by item code. Case-insensitive search."),
    quantity_unit: Optional[str] = Query(None, description="Filter by quantity unit (buah, lusin, kodi, dus, bal)."),
    service: InventoryService = Depends(get_inventory_service),
):
    """
    ### Retrieve all Inventory items.

    Provides a paginated and filterable list of all items in the inventory.
    """
    return await service.get_all(
        page=page,
        limit=limit,
        nama_barang=nama_barang,
        kode_barang=kode_barang,
        quantity_unit=quantity_unit,
    )

@router.get("/{kode_barang}", response_model=SingleInventoryResponse)
async def get_inventory_by_id(
    kode_barang: str,
    service: InventoryService = Depends(get_inventory_service),
):
    """
    ### Get a single Inventory item by kode_barang.

    Retrieve the details and current stock levels of a specific inventory item
    using its unique kode_barang.
    """
    return await service.get_by_id(kode_barang=kode_barang)

@router.put("/{kode_barang}", response_model=SingleInventoryResponse)
async def update_inventory(
    kode_barang: str,
    request_data: InventoryUpdateRequest,
    service: InventoryService = Depends(get_inventory_service),
):
    """
    ### Update an Inventory item.

    Modify the details of an existing inventory item, such as its name, quantity, or pricing.
    """
    return await service.update(kode_barang=kode_barang, inventory_update=request_data)

@router.delete("/{kode_barang}", response_model=BaseSingleResponse)
async def delete_inventory(
    kode_barang: str,
    service: InventoryService = Depends(get_inventory_service),
):
    """
    ### Delete an Inventory item.

    Permanently remove an inventory item from the database.
    **Warning**: This can fail if the item is referenced in existing transactions.
    """
    return await service.delete(kode_barang=kode_barang)