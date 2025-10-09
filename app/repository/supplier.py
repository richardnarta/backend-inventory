from typing import Optional, List, Tuple
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from app.model.supplier import Supplier
from app.schema.supplier.request import SupplierCreateRequest, SupplierUpdateRequest

class SupplierRepository:
    """
    Handles asynchronous database operations for the Supplier model.
    """
    def __init__(self, session: AsyncSession):
        """
        Initializes the repository with an asynchronous database session.

        Args:
            session: The SQLModel AsyncSession object.
        """
        self.session = session

    async def create(self, *, supplier_create: SupplierCreateRequest) -> Supplier:
        """
        Asynchronously creates a new supplier in the database.

        Args:
            supplier_create: The Pydantic schema with data for the new supplier.

        Returns:
            The newly created Supplier entity.
        """
        db_supplier = Supplier.model_validate(supplier_create)
        self.session.add(db_supplier)
        await self.session.commit()
        await self.session.refresh(db_supplier)
        return db_supplier

    async def get_by_id(self, *, supplier_id: int) -> Optional[Supplier]:
        """
        Asynchronously fetches a supplier by their primary key (ID).

        Args:
            supplier_id: The ID of the supplier to fetch.

        Returns:
            The Supplier entity if found, otherwise None.
        """
        return await self.session.get(Supplier, supplier_id)

    async def get_all(
        self,
        *,
        name: Optional[str] = None,
        page: int = 1,
        limit: int = 10
    ) -> Tuple[List[Supplier], int]:
        statement = select(Supplier)
        
        if name:
            statement = statement.where(Supplier.name.ilike(f"%{name}%"))

        count_statement = select(func.count()).select_from(statement.subquery())
        count_result = await self.session.execute(count_statement) # CORRECTED LINE
        total_count = count_result.one()[0]

        offset = (page - 1) * limit
        paginated_statement = statement.order_by(Supplier.id).offset(offset).limit(limit)
        
        items_result = await self.session.execute(paginated_statement) # CORRECTED LINE
        items = items_result.scalars().all()
        
        return list(items), total_count

    async def update(
        self,
        *, 
        db_supplier: Supplier,
        supplier_update: SupplierUpdateRequest
    ) -> Supplier:
        """
        Asynchronously updates an existing supplier in the database.

        Args:
            db_supplier: The existing Supplier entity to update.
            supplier_update: The Pydantic schema with the updated data.

        Returns:
            The updated Supplier entity.
        """
        update_data = supplier_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_supplier, key, value)
        
        self.session.add(db_supplier)
        await self.session.commit()
        await self.session.refresh(db_supplier)
        return db_supplier

    async def delete(self, *, db_supplier: Supplier) -> None:
        """
        Asynchronously deletes a supplier from the database.

        Args:
            db_supplier: The Supplier entity to delete.
        """
        await self.session.delete(db_supplier)
        await self.session.commit()