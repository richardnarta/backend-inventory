"""
Excel batch upload utility for inventory items
"""

from typing import List, Dict, Any, Tuple
import openpyxl
from fastapi import UploadFile, HTTPException, status
import io

# Mapping from Excel unit values to system QuantityUnit enum
UNIT_MAPPING = {
    # UPPERCASE ABBREVIATIONS
    "BAL": "Bal",
    "BH": "Buah",
    "BTG": "Batang",
    "DUS": "Dus",
    "GL": "Gulung",
    "KG": "Kilogram",
    "KTK": "Kotak",
    "LBR": "Lembar",
    "LS": "Lusin",
    "M": "Meter",
    "ONS": "Ons",
    "PAK": "Pak",
    "PCS": "Pcs",
    "PS": "Pasang",
    "SAK": "Sak",
    
    # LOWERCASE ABBREVIATIONS
    "bal": "Bal",
    "bh": "Buah",
    "btg": "Batang",
    "dus": "Dus",
    "gl": "Gulung",
    "kg": "Kilogram",
    "ktk": "Kotak",
    "lbr": "Lembar",
    "ls": "Lusin",
    "m": "Meter",
    "ons": "Ons",
    "pak": "Pak",
    "pcs": "Pcs",
    "ps": "Pasang",
    "sak": "Sak",
    
    # MIXED/FULL NAMES (Safeguard)
    "Bal": "Bal",
    "Buah": "Buah",
    "Batang": "Batang",
    "Dus": "Dus",
    "Gulung": "Gulung",
    "Kilogram": "Kilogram",
    "Kotak": "Kotak",
    "Lembar": "Lembar",
    "Lusin": "Lusin",
    "Meter": "Meter",
    "Ons": "Ons",
    "Pak": "Pak",
    "Pcs": "Pcs",
    "Pasang": "Pasang",
    "Sak": "Sak"
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


async def process_excel_file(file: UploadFile) -> Tuple[List[Dict[str, Any]], int, List[str], List[dict]]:
    """
    Process uploaded Excel file and extract inventory data.
    
    Args:
        file: Uploaded Excel file
        
    Returns:
        Tuple of (valid_items, skipped_count, new_units_added, errors)
        
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
        errors = []
        
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
                    errors.append({"row": row_idx, "kode_barang": kode_barang, "reason": "Nama barang kosong."})
                    continue
                
                # Map quantity_unit
                quantity_unit_str = str(quantity_unit_raw).strip() if quantity_unit_raw else ""
                quantity_unit = UNIT_MAPPING.get(quantity_unit_str)
                
                # Skip row if unit not mapped
                if not quantity_unit:
                    skipped_count += 1
                    errors.append({"row": row_idx, "kode_barang": kode_barang, "reason": f"Satuan '{quantity_unit_str}' tidak dikenal."})
                    continue
                
                # (no longer tracking new units — all valid units are in the enum)

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
                errors.append({"row": row_idx, "reason": f"Parsing error: {str(e)}"})
                continue
        
        return valid_items, skipped_count, list(new_units), errors
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing Excel file: {str(e)}"
        )
