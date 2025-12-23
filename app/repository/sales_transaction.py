from typing import Optional, List, Tuple
from datetime import datetime, date
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload

from app.model.sales_transaction import SalesTransaction
from app.schema.sales_transaction.request import (
    SalesTransactionCreateRequest,
    SalesTransactionUpdateRequest,
)

class SalesTransactionRepository:
    """
    Handles asynchronous database operations for the SalesTransaction model.
    """

    def __init__(self, session: AsyncSession):
        """
        Initializes the repository with an asynchronous database session.

        Args:
            session: The SQLModel AsyncSession object.
        """
        self.session = session

    async def create(
        self, *, st_create: SalesTransactionCreateRequest
    ) -> SalesTransaction:
        """
        Asynchronously creates a new sales transaction.
        The transaction_date is automatically set to the current timestamp if not provided.
        """
        create_data = st_create.model_dump()
        
        # Set transaction_date if not provided
        if 'transaction_date' not in create_data or not create_data.get('transaction_date'):
            create_data['transaction_date'] = datetime.now()
        
        # Auto-calculate total_price if not provided
        if 'total_price' not in create_data or create_data.get('total_price') is None:
            quantity = create_data.get('quantity', 0)
            price_per_unit = create_data.get('price_per_unit', 0)
            create_data['total_price'] = quantity * price_per_unit
        
        db_st = SalesTransaction(**create_data)
        self.session.add(db_st)
        await self.session.commit()
        await self.session.refresh(db_st)
        return db_st

    async def get_by_id(self, *, st_id: int) -> Optional[SalesTransaction]:
        """Get a sales transaction by ID with related buyer and inventory"""
        statement = (
            select(SalesTransaction)
            .where(SalesTransaction.id == st_id)
            .options(
                selectinload(SalesTransaction.buyer),
                selectinload(SalesTransaction.inventory),
            )
        )
        result = await self.session.execute(statement)
        return result.scalars().one_or_none()

    async def get_all(
        self,
        *,
        buyer_id: Optional[int] = None,
        inventory_id: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = 1,
        limit: int = 10,
    ) -> Tuple[List[SalesTransaction], int]:
        """Get all sales transactions with optional filters and pagination"""
        statement = select(SalesTransaction).options(
            selectinload(SalesTransaction.buyer),
            selectinload(SalesTransaction.inventory),
        )

        # Apply filters
        if buyer_id is not None:
            statement = statement.where(SalesTransaction.buyer_id == buyer_id)
        if inventory_id:
            statement = statement.where(SalesTransaction.inventory_id == inventory_id)
        if start_date:
            statement = statement.where(func.date(SalesTransaction.transaction_date) >= start_date)
        if end_date:
            statement = statement.where(func.date(SalesTransaction.transaction_date) <= end_date)

        # Get total count
        count_statement = select(func.count()).select_from(statement.subquery())
        count_result = await self.session.execute(count_statement)
        total_count = count_result.one()[0]

        # Apply pagination
        offset = (page - 1) * limit
        paginated_statement = (
            statement.order_by(SalesTransaction.id.desc()).offset(offset).limit(limit)
        )

        items_result = await self.session.execute(paginated_statement)
        items = items_result.scalars().all()

        return list(items), total_count

    async def update(
        self,
        *,
        db_st: SalesTransaction,
        st_update: SalesTransactionUpdateRequest,
    ) -> SalesTransaction:
        """
        Asynchronously updates an existing sales transaction.
        """
        update_data = st_update.model_dump(exclude_unset=True)
        
        # Update fields
        for key, value in update_data.items():
            setattr(db_st, key, value)
        
        # Recalculate total_price if quantity or price_per_unit changed
        if 'quantity' in update_data or 'price_per_unit' in update_data:
            if 'total_price' not in update_data:
                db_st.total_price = db_st.quantity * db_st.price_per_unit

        self.session.add(db_st)
        await self.session.commit()
        await self.session.refresh(db_st)
        return db_st

    async def delete(self, *, db_st: SalesTransaction) -> None:
        """
        Asynchronously deletes a sales transaction from the database.
        """
        await self.session.delete(db_st)
        await self.session.commit()