from typing import Optional, List, Tuple
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload

from app.model.account_receivable import AccountReceivable
from app.schema.account_receivable.request import (
    AccountReceivableCreateRequest,
    AccountReceivableUpdateRequest,
)

class AccountReceivableRepository:
    """
    Handles asynchronous database operations for the AccountReceivable model.
    """

    def __init__(self, session: AsyncSession):
        """
        Initializes the repository with an asynchronous database session.

        Args:
            session: The SQLModel AsyncSession object.
        """
        self.session = session

    async def create(
        self, *, ar_create: AccountReceivableCreateRequest
    ) -> AccountReceivable:
        """
        Asynchronously creates a new account receivable record.

        Args:
            ar_create: The Pydantic schema with data for the new record.

        Returns:
            The newly created AccountReceivable entity.
        """
        db_ar = AccountReceivable.model_validate(ar_create)
        self.session.add(db_ar)
        await self.session.commit()
        await self.session.refresh(db_ar)
        return db_ar

    async def get_by_id(self, *, ar_id: int) -> Optional[AccountReceivable]:
        # UPDATE THIS METHOD
        statement = (
            select(AccountReceivable)
            .where(AccountReceivable.id == ar_id)
            .options(selectinload(AccountReceivable.buyer))
        )
        result = await self.session.execute(statement)
        return result.scalars().one_or_none()

    async def get_all(
        self,
        *,
        buyer_id: Optional[int] = None,
        period: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
    ) -> Tuple[List[AccountReceivable], int]:
        # UPDATE THIS LINE
        statement = select(AccountReceivable).options(selectinload(AccountReceivable.buyer))

        if buyer_id is not None:
            statement = statement.where(AccountReceivable.buyer_id == buyer_id)
        if period:
            statement = statement.where(AccountReceivable.period.ilike(f"%{period}%"))

        count_statement = select(func.count()).select_from(statement.subquery())
        count_result = await self.session.execute(count_statement)
        total_count = count_result.scalar_one()

        offset = (page - 1) * limit
        paginated_statement = statement.order_by(AccountReceivable.id).offset(offset).limit(limit)

        items_result = await self.session.execute(paginated_statement)
        items = items_result.scalars().all()

        return list(items), total_count

    async def update(
        self,
        *,
        db_ar: AccountReceivable,
        ar_update: AccountReceivableUpdateRequest,
    ) -> AccountReceivable:
        """
        Asynchronously updates an existing account receivable record.

        Args:
            db_ar: The existing AccountReceivable entity to update.
            ar_update: The Pydantic schema with the updated data.

        Returns:
            The updated AccountReceivable entity.
        """
        update_data = ar_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_ar, key, value)

        self.session.add(db_ar)
        await self.session.commit()
        await self.session.refresh(db_ar)
        return db_ar

    async def delete(self, *, db_ar: AccountReceivable) -> None:
        """
        Asynchronously deletes an account receivable record from the database.

        Args:
            db_ar: The AccountReceivable entity to delete.
        """
        await self.session.delete(db_ar)
        await self.session.commit()