"""
Excel batch upload utility for inventory items
"""

from typing import List, Dict, Any, Tuple
import openpyxl
from fastapi import UploadFile, HTTPException, status
import io

# Mapping from Excel unit values to system QuantityUnit enum
UNIT_MAPPING = {
    "DUS": "Dus",
    "BTG": "Batang",
    "BAL": "Bal",
    "BH": "Pcs",
    "PCS": "Pcs",
    "dus": "Dus",
    "lbr": "Lembar",
    "LBR": "Lembar",
    "LEMBAR": "Lembar",
    "ls": "Lusin",
    "LS": "Lusin",
    "LUSIN": "Lusin",
    "m": "Meter",
    "M": "Meter",
    "METER": "Meter",
    "pak": "Pak",
    "PAK": "Pak",
    "ons": "Ons",
    "ONS": "Ons",
    "sak": "Sak",
    "SAK": "Sak",
    "BATANG": "Batang",
    "btg": "Batang",
    "bal": "Bal",
    "pcs": "Pcs",
    "bh": "Pcs",
    "lembar": "Lembar",
    "lusin": "Lusin",
    "meter": "Meter",
    "kotak": "Kotak",
    "KOTAK": "Kotak",
    "kg": "Kilogram",
    "KG": "Kilogram",
    "KILOGRAM": "Kilogram",
    "kilogram": "Kilogram",
}

# Expected column headers (for validation)
EXPECTED_COLUMNS = {
    'A': 'Kode Barang',
    'C': 'Nama Barang', 
    'F': 'Satuan',
    'G': 'Harga Modal',
    'H': 'Harga Jual Eceran',
    'I': 'Qty',
    'P': 'Keterangan'
}


async def process_excel_file(file: UploadFile) -> Tuple[List[Dict[str, Any]], int, List[str]]:
    """
    Process uploaded Excel file and extract inventory data.
    
    Args:
        file: Uploaded Excel file
        
    Returns:
        Tuple of (valid_items, skipped_count, new_units_added)
        
    Raises:
        HTTPException: If file format is invalid
    """
    # Validate file extension
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File harus berformat Excel (.xlsx atau .xls)"
        )
    
    try:
        # Read file content
        contents = await file.read()
        workbook = openpyxl.load_workbook(io.BytesIO(contents), data_only=True)
        sheet = workbook.active
        
        # Validate headers (row 1 and 2)
        # We can optionally validate column headers here if needed
        
        valid_items = []
        skipped_count = 0
        new_units = set()
        
        # Process data starting from row 3
        for row_idx in range(3, sheet.max_row + 1):
            try:
                # Extract cell values
                kode_barang = sheet[f'A{row_idx}'].value
                nama_barang = sheet[f'C{row_idx}'].value
                quantity_unit_raw = sheet[f'F{row_idx}'].value
                harga_modal = sheet[f'G{row_idx}'].value
                harga_jual_eceran = sheet[f'H{row_idx}'].value
                quantity = sheet[f'I{row_idx}'].value
                additional_note = sheet[f'P{row_idx}'].value
                
                # Skip if kode_barang is empty (end of data)
                if not kode_barang:
                    continue
                
                # Skip if nama_barang is empty
                if not nama_barang:
                    skipped_count += 1
                    continue
                
                # Map quantity_unit
                quantity_unit_str = str(quantity_unit_raw).strip() if quantity_unit_raw else ""
                quantity_unit = UNIT_MAPPING.get(quantity_unit_str)
                
                # Skip row if unit not mapped
                if not quantity_unit:
                    skipped_count += 1
                    continue
                
                # Track new units that might not be in the enum yet
                if quantity_unit in ["Lusin", "Ons"]:
                    new_units.add(quantity_unit)
                
                # Prepare item data
                item_data = {
                    "kode_barang": str(kode_barang).strip().replace(' ', '_').upper(),
                    "nama_barang": str(nama_barang).strip(),
                    "quantity": float(quantity) if quantity else 0.0,
                    "quantity_unit": quantity_unit,
                    "harga_modal": float(harga_modal) if harga_modal else 0.0,
                    "harga_jual_eceran": float(harga_jual_eceran) if harga_jual_eceran else 0.0,
                    "harga_jual_grosir": 0.0,  # Default value, can be updated later
                    "additional_note": str(additional_note).strip() if additional_note else ""
                }
                
                valid_items.append(item_data)
                
            except Exception as e:
                # Skip rows with parsing errors
                skipped_count += 1
                continue
        
        return valid_items, skipped_count, list(new_units)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing Excel file: {str(e)}"
        )
