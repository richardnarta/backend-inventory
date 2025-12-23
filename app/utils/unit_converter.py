"""
Unit Conversion Utility for Inventory Management

Base unit: buah (pieces)
All conversions are relative to 'buah'

Conversion constants can be adjusted based on business needs:
- dus: Default is 48 buah (4 lusin) - typical for small boxes
- bal: Default is 240 buah (20 lusin) - typical for bales/bundles in textile

Feel free to modify the constants below to match your business requirements.
"""

from app.model.inventory import QuantityUnit

# ============================================
# CONVERSION CONSTANTS (Edit as needed)
# ============================================

# Base conversions to 'buah' (pieces)
UNIT_TO_BASE_MULTIPLIER = {
    QuantityUnit.BUAH: 1,      # 1 buah = 1 unit (base)
    QuantityUnit.LUSIN: 12,    # 1 lusin = 12 buah
    QuantityUnit.KODI: 20,     # 1 kodi = 20 buah
    QuantityUnit.DUS: 48,      # 1 dus = 48 buah (4 lusin) - EDITABLE
    QuantityUnit.BAL: 240,     # 1 bal = 240 buah (20 lusin) - EDITABLE
}

# ============================================
# CONVERSION FUNCTIONS
# ============================================

def convert_to_base_unit(quantity: float, from_unit: QuantityUnit) -> float:
    """
    Convert a quantity from any unit to base unit (buah)
    
    Args:
        quantity: The amount to convert
        from_unit: The source unit
        
    Returns:
        float: Quantity in base units (buah)
        
    Example:
        convert_to_base_unit(2, QuantityUnit.LUSIN) -> 24.0
        convert_to_base_unit(3, QuantityUnit.KODI) -> 60.0
    """
    multiplier = UNIT_TO_BASE_MULTIPLIER.get(from_unit, 1)
    return quantity * multiplier


def convert_from_base_unit(quantity_in_base: float, to_unit: QuantityUnit) -> float:
    """
    Convert a quantity from base unit (buah) to target unit
    
    Args:
        quantity_in_base: Quantity in base units (buah)
        to_unit: The target unit
        
    Returns:
        float: Quantity in target unit
        
    Example:
        convert_from_base_unit(24, QuantityUnit.LUSIN) -> 2.0
        convert_from_base_unit(60, QuantityUnit.KODI) -> 3.0
    """
    multiplier = UNIT_TO_BASE_MULTIPLIER.get(to_unit, 1)
    if multiplier == 0:
        return 0
    return quantity_in_base / multiplier


def convert_quantity(
    quantity: float,
    from_unit: QuantityUnit,
    to_unit: QuantityUnit
) -> float:
    """
    Convert quantity from one unit to another
    
    Args:
        quantity: The amount to convert
        from_unit: The source unit
        to_unit: The target unit
        
    Returns:
        float: Converted quantity in target unit
        
    Example:
        # Convert 2 kodi to lusin
        convert_quantity(2, QuantityUnit.KODI, QuantityUnit.LUSIN)
        # -> 2 kodi = 40 buah = 3.33 lusin
        
        # Convert 1 dus to lusin
        convert_quantity(1, QuantityUnit.DUS, QuantityUnit.LUSIN)
        # -> 1 dus = 48 buah = 4 lusin
    """
    # If same unit, no conversion needed
    if from_unit == to_unit:
        return quantity
    
    # Convert to base unit first, then to target unit
    quantity_in_base = convert_to_base_unit(quantity, from_unit)
    return convert_from_base_unit(quantity_in_base, to_unit)


def add_quantity_to_inventory(
    inventory_quantity: float,
    inventory_unit: QuantityUnit,
    add_quantity: float,
    add_unit: QuantityUnit
) -> float:
    """
    Add a quantity to inventory, converting units if necessary
    
    Args:
        inventory_quantity: Current inventory quantity
        inventory_unit: Current inventory unit
        add_quantity: Quantity to add
        add_unit: Unit of quantity to add
        
    Returns:
        float: New inventory quantity (in inventory_unit)
        
    Example:
        # Inventory has 23 lusin, add 2 kodi
        add_quantity_to_inventory(23, QuantityUnit.LUSIN, 2, QuantityUnit.KODI)
        # -> 23 + (40/12) = 23 + 3.33 = 26.33 lusin
    """
    converted_quantity = convert_quantity(add_quantity, add_unit, inventory_unit)
    return inventory_quantity + converted_quantity


def subtract_quantity_from_inventory(
    inventory_quantity: float,
    inventory_unit: QuantityUnit,
    subtract_quantity: float,
    subtract_unit: QuantityUnit
) -> float:
    """
    Subtract a quantity from inventory, converting units if necessary
    
    Args:
        inventory_quantity: Current inventory quantity
        inventory_unit: Current inventory unit
        subtract_quantity: Quantity to subtract
        subtract_unit: Unit of quantity to subtract
        
    Returns:
        float: New inventory quantity (in inventory_unit)
        
    Example:
        # Inventory has 26.33 lusin, subtract 1.5 kodi
        subtract_quantity_from_inventory(26.33, QuantityUnit.LUSIN, 1.5, QuantityUnit.KODI)
        # -> 26.33 - (30/12) = 26.33 - 2.5 = 23.83 lusin
    """
    converted_quantity = convert_quantity(subtract_quantity, subtract_unit, inventory_unit)
    return inventory_quantity - converted_quantity
