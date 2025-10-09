from typing import Optional, List, Tuple
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload

from app.model.buyer import Buyer
from app.model.account_receivable import AccountReceivable # Import AccountReceivable
from app.schema.buyer.request import BuyerCreateRequest, BuyerUpdateRequest

class BuyerRepository:
    """
    Handles asynchronous database operations for the Buyer model.
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, *, buyer_create: BuyerCreateRequest) -> Buyer:
        # This method remains the same
        db_buyer = Buyer.model_validate(buyer_create)
        self.session.add(db_buyer)
        await self.session.commit()
        await self.session.refresh(db_buyer)
        return db_buyer

    async def get_by_id(self, *, buyer_id: int) -> Optional[Tuple[Buyer, bool]]:
        is_risked_subquery = (
            select(AccountReceivable)
            .where(
                AccountReceivable.buyer_id == Buyer.id,
                AccountReceivable.age_over_90_days > 0,
            )
            .exists()
            .label("is_risked")
        )
        
        statement = select(Buyer, is_risked_subquery).where(Buyer.id == buyer_id)
        result = await self.session.execute(statement) # CORRECTED LINE
        return result.one_or_none()

    async def get_all(
        self,
        *,
        name: Optional[str] = None,
        page: int = 1,
        limit: int = 10
    ) -> Tuple[List[Tuple[Buyer, bool]], int]:
        is_risked_subquery = (
            select(AccountReceivable)
            .where(
                AccountReceivable.buyer_id == Buyer.id,
                AccountReceivable.age_over_90_days > 0,
            )
            .exists()
            .label("is_risked")
        )

        statement = select(Buyer, is_risked_subquery)
        
        if name:
            statement = statement.where(Buyer.name.ilike(f"%{name}%"))

        count_statement = select(func.count()).select_from(statement.subquery())
        count_result = await self.session.execute(count_statement) # CORRECTED LINE
        total_count = count_result.one()[0]

        offset = (page - 1) * limit
        paginated_statement = statement.order_by(Buyer.id).offset(offset).limit(limit)
        
        items_result = await self.session.execute(paginated_statement) # CORRECTED LINE
        items = items_result.all()
        
        return items, total_count

    async def update(self, *, db_buyer: Buyer, buyer_update: BuyerUpdateRequest) -> Buyer:
        # This method remains the same
        update_data = buyer_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_buyer, key, value)
        
        self.session.add(db_buyer)
        await self.session.commit()
        await self.session.refresh(db_buyer)
        return db_buyer

    async def delete(self, *, db_buyer: Buyer) -> None:
        # This method remains the same
        await self.session.delete(db_buyer)
        await self.session.commit()