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
        The transaction_date is automatically set to the current timestamp.

        Args:
            st_create: The Pydantic schema with data for the new transaction.

        Returns:
            The newly created SalesTransaction entity.
        """
        create_data = st_create.model_dump()
        db_st = SalesTransaction(**create_data, transaction_date=datetime.now())
        self.session.add(db_st)
        await self.session.commit()
        await self.session.refresh(db_st)
        return db_st

    async def get_by_id(self, *, st_id: int) -> Optional[SalesTransaction]:
        # UPDATE THIS METHOD
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
        statement = select(SalesTransaction).options(
            selectinload(SalesTransaction.buyer),
            selectinload(SalesTransaction.inventory),
        )

        if buyer_id is not None:
            statement = statement.where(SalesTransaction.buyer_id == buyer_id)
        if inventory_id:
            statement = statement.where(SalesTransaction.inventory_id == inventory_id)
        if start_date:
            statement = statement.where(func.date(SalesTransaction.transaction_date) >= start_date)
        if end_date:
            statement = statement.where(func.date(SalesTransaction.transaction_date) <= end_date)

        count_statement = select(func.count()).select_from(statement.subquery())
        count_result = await self.session.execute(count_statement) # CORRECTED LINE
        total_count = count_result.one()[0]

        offset = (page - 1) * limit
        paginated_statement = (
            statement.order_by(SalesTransaction.id.desc()).offset(offset).limit(limit)
        )

        items_result = await self.session.execute(paginated_statement) # CORRECTED LINE
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

        Args:
            db_st: The existing SalesTransaction entity to update.
            st_update: The Pydantic schema with the updated data.

        Returns:
            The updated SalesTransaction entity.
        """
        update_data = st_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_st, key, value)

        self.session.add(db_st)
        await self.session.commit()
        await self.session.refresh(db_st)
        return db_st

    async def delete(self, *, db_st: SalesTransaction) -> None:
        """
        Asynchronously deletes a sales transaction from the database.

        Args:
            db_st: The SalesTransaction entity to delete.
        """
        await self.session.delete(db_st)
        await self.session.commit()