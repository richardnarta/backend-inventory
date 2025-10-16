from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime, date
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload

from app.model.inventory import Inventory
from app.model.purchase_transaction import PurchaseTransaction
from app.schema.purchase_transaction.request import (
    PurchaseTransactionCreateRequest,
    PurchaseTransactionUpdateRequest,
)

class PurchaseTransactionRepository:
    """
    Handles asynchronous database operations for the PurchaseTransaction model.
    """

    def __init__(self, session: AsyncSession):
        """
        Initializes the repository with an asynchronous database session.

        Args:
            session: The SQLModel AsyncSession object.
        """
        self.session = session

    async def create(
        self, *, pt_create_data: Dict[str, Any]
    ) -> PurchaseTransaction:
        """
        Asynchronously creates a new purchase transaction from a dictionary.
        The service layer is responsible for providing all necessary data.
        """
        # Ensure transaction_date is set if not provided by the service
        if 'transaction_date' not in pt_create_data or not pt_create_data.get('transaction_date'):
            pt_create_data['transaction_date'] = datetime.now()
        
        # Create the model instance directly from the dictionary
        db_pt = PurchaseTransaction(**pt_create_data)
        self.session.add(db_pt)
        await self.session.commit()
        await self.session.refresh(db_pt)
        return db_pt

    async def get_by_id(self, *, pt_id: int) -> Optional[PurchaseTransaction]:
        # UPDATE THIS METHOD
        statement = (
            select(PurchaseTransaction)
            .where(PurchaseTransaction.id == pt_id)
            .options(
                selectinload(PurchaseTransaction.supplier),
                selectinload(PurchaseTransaction.inventory),
            )
        )
        result = await self.session.execute(statement)
        return result.scalars().one_or_none()

    async def get_all(
        self,
        *,
        supplier_id: Optional[int] = None,
        inventory_id: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = 1,
        limit: int = 10,
        inventory_type: Optional[str] = None,
    ) -> Tuple[List[PurchaseTransaction], int]:
        statement = (
            select(PurchaseTransaction)
            .join(Inventory) # <-- TAMBAHKAN JOIN DI SINI
            .options(
                selectinload(PurchaseTransaction.supplier),
                selectinload(PurchaseTransaction.inventory),
            )
        )

        if supplier_id is not None:
            statement = statement.where(PurchaseTransaction.supplier_id == supplier_id)
        if inventory_id:
            statement = statement.where(PurchaseTransaction.inventory_id == inventory_id)
        if start_date:
            statement = statement.where(func.date(PurchaseTransaction.transaction_date) >= start_date)
        if end_date:
            statement = statement.where(func.date(PurchaseTransaction.transaction_date) <= end_date)
        if inventory_type:
            statement = statement.where(Inventory.type == inventory_type)

        count_statement = select(func.count()).select_from(statement.subquery())
        count_result = await self.session.execute(count_statement) # CORRECTED LINE
        total_count = count_result.one()[0]

        offset = (page - 1) * limit
        paginated_statement = (
            statement.order_by(PurchaseTransaction.id.desc()).offset(offset).limit(limit)
        )

        items_result = await self.session.execute(paginated_statement) # CORRECTED LINE
        items = items_result.scalars().all()

        return list(items), total_count

    async def update(
        self,
        *,
        db_pt: PurchaseTransaction,
        pt_update: PurchaseTransactionUpdateRequest,
    ) -> PurchaseTransaction:
        """
        Asynchronously updates an existing purchase transaction.

        Args:
            db_pt: The existing PurchaseTransaction entity to update.
            pt_update: The Pydantic schema with the updated data.

        Returns:
            The updated PurchaseTransaction entity.
        """
        update_data = pt_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_pt, key, value)

        self.session.add(db_pt)
        await self.session.commit()
        await self.session.refresh(db_pt)
        return db_pt

    async def delete(self, *, db_pt: PurchaseTransaction) -> None:
        """
        Asynchronously deletes a purchase transaction from the database.

        Args:
            db_pt: The PurchaseTransaction entity to delete.
        """
        await self.session.delete(db_pt)
        await self.session.commit()