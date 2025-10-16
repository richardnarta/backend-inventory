# app/repository/inventory.py

from typing import Optional, List, Tuple
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from app.model.inventory import Inventory, InventoryType
from app.schema.inventory.request import InventoryUpdateRequest

# Definisikan konstanta rasio di sini agar bisa diakses
BALE_TO_KG_RATIO = 181.44

class InventoryRepository:
    # ... (metode __init__, create, get_by_id, dll. tidak berubah) ...
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, *, db_inventory: Inventory) -> Inventory:
        self.session.add(db_inventory)
        await self.session.commit()
        await self.session.refresh(db_inventory)
        return db_inventory

    async def get_by_id(self, *, inventory_id: str) -> Optional[Inventory]:
        return await self.session.get(Inventory, inventory_id)
        
    async def get_by_ids(self, *, inventory_ids: List[str]) -> List[Inventory]:
        statement = select(Inventory).where(Inventory.id.in_(inventory_ids))
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_all(
        self,
        *,
        name: Optional[str] = None,
        id: Optional[str] = None,
        type: Optional[str] = None,
        page: int = 1,
        limit: int = 10
    ) -> Tuple[List[Inventory], int]:
        statement = select(Inventory)
        
        if name:
            statement = statement.where(Inventory.name.ilike(f"%{name}%"))
        if id:
            statement = statement.where(Inventory.id.ilike(f"%{id}%"))
        if type:
            statement = statement.where(Inventory.type == type)

        count_statement = select(func.count()).select_from(statement.subquery())
        count_result = await self.session.execute(count_statement)
        total_count = count_result.scalar_one()

        offset = (page - 1) * limit
        paginated_statement = statement.offset(offset).limit(limit)
        
        items_result = await self.session.execute(paginated_statement)
        items = items_result.scalars().all()
        
        return list(items), total_count

    async def update(
        self,
        *, 
        db_inventory: Inventory,
        inventory_update: InventoryUpdateRequest
    ) -> Inventory:
        """
        Updates an inventory item and automatically recalculates bale_count
        using a fallback ratio if the item's own ratio is not set.
        """
        update_data = inventory_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_inventory, key, value)
        
        # --- LOGIKA KALKULASI YANG DIPERBARUI ---
        if db_inventory.type == InventoryType.THREAD:
            weight_kg = db_inventory.weight_kg or 0
            
            # Gunakan bale_ratio dari item jika valid, jika tidak, gunakan konstanta standar
            # `or` akan memilih nilai pertama yang "truthy" (bukan 0, None, False)
            
            # Perhitungan tetap aman dari pembagian dengan nol
            db_inventory.bale_count = round((weight_kg / BALE_TO_KG_RATIO), 3)
        # --------------------------------------------------------
        
        self.session.add(db_inventory)
        await self.session.commit()
        await self.session.refresh(db_inventory)
        return db_inventory

    async def delete(self, *, db_inventory: Inventory) -> None:
        await self.session.delete(db_inventory)
        await self.session.commit()