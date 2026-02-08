from typing import Optional, List, Tuple
from datetime import date
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload

from app.model.sales_transaction import SalesTransaction, SalesTransactionItem


class SalesTransactionRepository:
    """
    Handles asynchronous database operations for SalesTransaction (header-detail pattern).
    """

    def __init__(self, session: AsyncSession):
        """
        Initializes the repository with an asynchronous database session.

        Args:
            session: The SQLModel AsyncSession object.
        """
        self.session = session

    async def create_header(self, transaction_data: dict) -> SalesTransaction:
        """
        Creates a new sales transaction header.
        
        Args:
            transaction_data: Dictionary containing header fields (transaction_date, buyer_id, notes, total_amount)
        
        Returns:
            Created SalesTransaction header
        """
        db_transaction = SalesTransaction(**transaction_data)
        self.session.add(db_transaction)
        await self.session.commit()
        await self.session.refresh(db_transaction)
        return db_transaction

    async def create_item(self, item_data: dict) -> SalesTransactionItem:
        """
        Creates a new sales transaction item.
        
        Args:
            item_data: Dictionary containing item fields
        
        Returns:
            Created SalesTransactionItem
        """
        db_item = SalesTransactionItem(**item_data)
        self.session.add(db_item)
        await self.session.commit()
        await self.session.refresh(db_item)
        return db_item

    async def get_by_id(self, *, st_id: int) -> Optional[SalesTransaction]:
        """
        Get a sales transaction by ID with related buyer and items.
        Items are eagerly loaded with their inventory data.
        """
        statement = (
            select(SalesTransaction)
            .where(SalesTransaction.id == st_id)
            .options(
                selectinload(SalesTransaction.buyer),
                selectinload(SalesTransaction.items).selectinload(SalesTransactionItem.inventory),
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
        """
        Get all sales transactions with optional filters and pagination.
        Eagerly loads buyer and items with inventory.
        """
        statement = (
            select(SalesTransaction)
            .options(
                selectinload(SalesTransaction.buyer),
                selectinload(SalesTransaction.items).selectinload(SalesTransactionItem.inventory),
            )
        )

        # Apply filters
        if buyer_id is not None:
            statement = statement.where(SalesTransaction.buyer_id == buyer_id)
        
        # Filter by inventory_id requires joining with items
        if inventory_id:
            statement = statement.join(SalesTransactionItem).where(
                SalesTransactionItem.inventory_id == inventory_id
            )
        
        if start_date:
            statement = statement.where(func.date(SalesTransaction.transaction_date) >= start_date)
        if end_date:
            statement = statement.where(func.date(SalesTransaction.transaction_date) <= end_date)

        # Get total count
        count_statement = select(func.count()).select_from(statement.subquery())
        count_result = await self.session.execute(count_statement)
        total_count = count_result.one()[0]

        # Apply pagination and ordering
        offset = (page - 1) * limit
        paginated_statement = (
            statement.order_by(SalesTransaction.transaction_date.desc()).offset(offset).limit(limit)
        )

        items_result = await self.session.execute(paginated_statement)
        items = items_result.scalars().all()

        return list(items), total_count

    async def update_header(self, db_st: SalesTransaction, update_data: dict) -> SalesTransaction:
        """
        Updates a sales transaction header.
        
        Args:
            db_st: Existing SalesTransaction instance
            update_data: Dictionary of fields to update
        
        Returns:
            Updated SalesTransaction
        """
        for key, value in update_data.items():
            setattr(db_st, key, value)
        
        self.session.add(db_st)
        await self.session.commit()
        await self.session.refresh(db_st)
        return db_st

    async def delete_all_items(self, transaction_id: int) -> None:
        """
        Deletes all items for a given transaction.
        Used when updating transaction items (delete old, create new).
        
        Args:
            transaction_id: The sales transaction ID
        """
        statement = select(SalesTransactionItem).where(
            SalesTransactionItem.sales_transaction_id == transaction_id
        )
        result = await self.session.execute(statement)
        items = result.scalars().all()
        
        for item in items:
            await self.session.delete(item)
        
        await self.session.commit()

    async def delete(self, *, db_st: SalesTransaction) -> None:
        """
        Deletes a sales transaction (header and all items via CASCADE).
        """
        await self.session.delete(db_st)
        await self.session.commit()