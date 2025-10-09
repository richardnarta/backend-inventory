from typing import Optional, List, Tuple
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from app.model.inventory import Inventory
from app.schema.inventory.request import InventoryCreateRequest, InventoryUpdateRequest

class InventoryRepository:
    """
    Handles asynchronous database operations for the Inventory model.
    """
    def __init__(self, session: AsyncSession):
        """
        Initializes the repository with an asynchronous database session.

        Args:
            session: The SQLModel AsyncSession object.
        """
        self.session = session

    async def create(self, *, inventory_create: InventoryCreateRequest) -> Inventory:
        """
        Asynchronously creates a new inventory item in the database.

        Args:
            inventory_create: The Pydantic schema with data for the new inventory item.

        Returns:
            The newly created Inventory entity.
        """
        db_inventory = Inventory.model_validate(inventory_create)
        self.session.add(db_inventory)
        await self.session.commit()
        await self.session.refresh(db_inventory)
        return db_inventory

    async def get_by_id(self, *, inventory_id: str) -> Optional[Inventory]:
        """
        Asynchronously fetches an inventory item by its primary key (ID).

        Args:
            inventory_id: The ID of the inventory item to fetch.

        Returns:
            The Inventory entity if found, otherwise None.
        """
        return await self.session.get(Inventory, inventory_id)
        
    async def get_by_ids(self, *, inventory_ids: List[str]) -> List[Inventory]:
        statement = select(Inventory).where(Inventory.id.in_(inventory_ids))
        result = await self.session.execute(statement) # CORRECTED LINE
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
        count_result = await self.session.execute(count_statement) # CORRECTED LINE
        total_count = count_result.one()[0]

        offset = (page - 1) * limit
        paginated_statement = statement.offset(offset).limit(limit)
        
        items_result = await self.session.execute(paginated_statement) # CORRECTED LINE
        items = items_result.scalars().all()
        
        return list(items), total_count

    async def update(
        self,
        *, 
        db_inventory: Inventory,
        inventory_update: InventoryUpdateRequest
    ) -> Inventory:
        """
        Asynchronously updates an existing inventory item in the database.

        Args:
            db_inventory: The existing Inventory entity to update.
            inventory_update: The Pydantic schema with the updated data.

        Returns:
            The updated Inventory entity.
        """
        update_data = inventory_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_inventory, key, value)
        
        self.session.add(db_inventory)
        await self.session.commit()
        await self.session.refresh(db_inventory)
        return db_inventory

    async def delete(self, *, db_inventory: Inventory) -> None:
        """
        Asynchronously deletes an inventory item from the database.

        Args:
            db_inventory: The Inventory entity to delete.
        """
        await self.session.delete(db_inventory)
        await self.session.commit()