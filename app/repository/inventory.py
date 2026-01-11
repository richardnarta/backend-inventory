# app/repository/inventory.py

from typing import Optional, List, Tuple
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from app.model.inventory import Inventory
from app.schema.inventory.request import InventoryUpdateRequest


class InventoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, *, db_inventory: Inventory) -> Inventory:
        self.session.add(db_inventory)
        await self.session.commit()
        await self.session.refresh(db_inventory)
        return db_inventory

    async def get_by_id(self, *, kode_barang: str) -> Optional[Inventory]:
        """Get inventory by kode_barang (primary key)"""
        return await self.session.get(Inventory, kode_barang)
        
    async def get_by_ids(self, *, kode_barangs: List[str]) -> List[Inventory]:
        """Get multiple inventory items by their kode_barang"""
        statement = select(Inventory).where(Inventory.kode_barang.in_(kode_barangs))
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_all(
        self,
        *,
        nama_barang: Optional[str] = None,
        kode_barang: Optional[str] = None,
        quantity_unit: Optional[str] = None,
        page: int = 1,
        limit: int = 10
    ) -> Tuple[List[Inventory], int]:
        """Get all inventory items with optional filters and pagination"""
        statement = select(Inventory)
        
        # Apply filters
        if nama_barang:
            statement = statement.where(Inventory.nama_barang.ilike(f"%{nama_barang}%"))
        if kode_barang:
            statement = statement.where(Inventory.kode_barang.ilike(f"%{kode_barang}%"))
        if quantity_unit:
            statement = statement.where(Inventory.quantity_unit == quantity_unit)

        # Get total count
        count_statement = select(func.count()).select_from(statement.subquery())
        count_result = await self.session.execute(count_statement)
        total_count = count_result.scalar_one()

        # Apply pagination and ordering
        offset = (page - 1) * limit
        paginated_statement = statement.order_by(Inventory.nama_barang.asc()).offset(offset).limit(limit)
        
        items_result = await self.session.execute(paginated_statement)
        items = items_result.scalars().all()
        
        return list(items), total_count

    async def update(
        self,
        *, 
        db_inventory: Inventory,
        inventory_update: InventoryUpdateRequest
    ) -> Inventory:
        """Update an inventory item with provided data"""
        update_data = inventory_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_inventory, key, value)
        
        self.session.add(db_inventory)
        await self.session.commit()
        await self.session.refresh(db_inventory)
        return db_inventory
    
    async def update_by_kode(
        self,
        *,
        kode_barang: str,
        update_data: dict
    ) -> Optional[Inventory]:
        """
        Convenience method to update inventory by kode_barang with dict data.
        Useful for stock quantity updates from transactions.
        """
        db_inventory = await self.get_by_id(kode_barang=kode_barang)
        if not db_inventory:
            return None
        
        for key, value in update_data.items():
            setattr(db_inventory, key, value)
        
        self.session.add(db_inventory)
        await self.session.commit()
        await self.session.refresh(db_inventory)
        return db_inventory

    async def delete(self, *, db_inventory: Inventory) -> None:
        """Delete an inventory item"""
        await self.session.delete(db_inventory)
        await self.session.commit()