from typing import Optional, List, Tuple
from datetime import date
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload

from app.model.purchase_transaction import PurchaseTransaction, PurchaseTransactionItem


class PurchaseTransactionRepository:
    """
    Handles asynchronous database operations for PurchaseTransaction (header-detail pattern).
    """

    def __init__(self, session: AsyncSession):
        """
        Initializes the repository with an asynchronous database session.

        Args:
            session: The SQLModel AsyncSession object.
        """
        self.session = session

    async def create_header(self, transaction_data: dict) -> PurchaseTransaction:
        """
        Creates a new purchase transaction header.
        
        Args:
            transaction_data: Dictionary containing header fields (transaction_date, supplier_id, notes, total_amount)
        
        Returns:
            Created PurchaseTransaction header
        """
        db_transaction = PurchaseTransaction(**transaction_data)
        self.session.add(db_transaction)
        await self.session.commit()
        await self.session.refresh(db_transaction)
        return db_transaction

    async def create_item(self, item_data: dict) -> PurchaseTransactionItem:
        """
        Creates a new purchase transaction item.
        
        Args:
            item_data: Dictionary containing item fields
        
        Returns:
            Created PurchaseTransactionItem
        """
        db_item = PurchaseTransactionItem(**item_data)
        self.session.add(db_item)
        await self.session.commit()
        await self.session.refresh(db_item)
        return db_item

    async def get_by_id(self, *, pt_id: int) -> Optional[PurchaseTransaction]:
        """
        Get a purchase transaction by ID with related supplier and items.
        Items are eagerly loaded with their inventory data.
        """
        statement = (
            select(PurchaseTransaction)
            .where(PurchaseTransaction.id == pt_id)
            .options(
                selectinload(PurchaseTransaction.supplier),
                selectinload(PurchaseTransaction.items).selectinload(PurchaseTransactionItem.inventory),
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
    ) -> Tuple[List[PurchaseTransaction], int]:
        """
        Get all purchase transactions with optional filters and pagination.
        Eagerly loads supplier and items with inventory.
        """
        statement = (
            select(PurchaseTransaction)
            .options(
                selectinload(PurchaseTransaction.supplier),
                selectinload(PurchaseTransaction.items).selectinload(PurchaseTransactionItem.inventory),
            )
        )

        # Apply filters
        if supplier_id is not None:
            statement = statement.where(PurchaseTransaction.supplier_id == supplier_id)
        
        # Filter by inventory_id requires joining with items
        if inventory_id:
            statement = statement.join(PurchaseTransactionItem).where(
                PurchaseTransactionItem.inventory_id == inventory_id
            )
        
        if start_date:
            statement = statement.where(func.date(PurchaseTransaction.transaction_date) >= start_date)
        if end_date:
            statement = statement.where(func.date(PurchaseTransaction.transaction_date) <= end_date)

        # Get total count
        count_statement = select(func.count()).select_from(statement.subquery())
        count_result = await self.session.execute(count_statement)
        total_count = count_result.one()[0]

        # Apply pagination and ordering
        offset = (page - 1) * limit
        paginated_statement = (
            statement.order_by(PurchaseTransaction.transaction_date.desc()).offset(offset).limit(limit)
        )

        items_result = await self.session.execute(paginated_statement)
        items = items_result.scalars().all()

        return list(items), total_count

    async def update_header(self, db_pt: PurchaseTransaction, update_data: dict) -> PurchaseTransaction:
        """
        Updates a purchase transaction header.
        
        Args:
            db_pt: Existing PurchaseTransaction instance
            update_data: Dictionary of fields to update
        
        Returns:
            Updated PurchaseTransaction
        """
        for key, value in update_data.items():
            setattr(db_pt, key, value)
        
        self.session.add(db_pt)
        await self.session.commit()
        await self.session.refresh(db_pt)
        return db_pt

    async def delete_all_items(self, transaction_id: int) -> None:
        """
        Deletes all items for a given transaction.
        Used when updating transaction items (delete old, create new).
        
        Args:
            transaction_id: The purchase transaction ID
        """
        statement = select(PurchaseTransactionItem).where(
            PurchaseTransactionItem.purchase_transaction_id == transaction_id
        )
        result = await self.session.execute(statement)
        items = result.scalars().all()
        
        for item in items:
            await self.session.delete(item)
        
        await self.session.commit()

    async def delete(self, *, db_pt: PurchaseTransaction) -> None:
        """
        Deletes a purchase transaction (header and all items via CASCADE).
        """
        await self.session.delete(db_pt)
        await self.session.commit()