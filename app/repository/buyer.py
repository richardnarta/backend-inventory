from typing import Optional, List, Tuple
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from app.model.buyer import Buyer
from app.schema.buyer.request import BuyerCreateRequest, BuyerUpdateRequest

class BuyerRepository:
    """
    Handles asynchronous database operations for the Buyer model.
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, *, buyer_create: BuyerCreateRequest) -> Buyer:
        """Create a new buyer"""
        db_buyer = Buyer.model_validate(buyer_create)
        self.session.add(db_buyer)
        await self.session.commit()
        await self.session.refresh(db_buyer)
        return db_buyer

    async def get_by_id(self, *, buyer_id: int) -> Optional[Buyer]:
        """Get a buyer by ID"""
        statement = select(Buyer).where(Buyer.id == buyer_id)
        result = await self.session.execute(statement)
        return result.scalars().one_or_none()

    async def get_all(
        self,
        *,
        name: Optional[str] = None,
        page: int = 1,
        limit: int = 10
    ) -> Tuple[List[Buyer], int]:
        """Get all buyers with optional filters and pagination"""
        statement = select(Buyer)
        
        if name:
            statement = statement.where(Buyer.name.ilike(f"%{name}%"))

        # Get total count
        count_statement = select(func.count()).select_from(statement.subquery())
        count_result = await self.session.execute(count_statement)
        total_count = count_result.one()[0]

        # Apply pagination and ordering
        offset = (page - 1) * limit
        paginated_statement = statement.order_by(Buyer.name.asc()).offset(offset).limit(limit)
        
        items_result = await self.session.execute(paginated_statement)
        items = items_result.scalars().all()
        
        return list(items), total_count

    async def update(self, *, db_buyer: Buyer, buyer_update: BuyerUpdateRequest) -> Buyer:
        """Update an existing buyer"""
        update_data = buyer_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_buyer, key, value)
        
        self.session.add(db_buyer)
        await self.session.commit()
        await self.session.refresh(db_buyer)
        return db_buyer

    async def delete(self, *, db_buyer: Buyer) -> None:
        """Delete a buyer"""
        await self.session.delete(db_buyer)
        await self.session.commit()