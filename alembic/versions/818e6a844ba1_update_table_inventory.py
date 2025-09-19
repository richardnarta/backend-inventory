"""update table inventory

Revision ID: 818e6a844ba1
Revises: 40de804c9725
Create Date: 2025-09-15 23:33:19.197839

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from app.model.inventory import InventoryType 


# revision identifiers, used by Alembic.
revision: str = '818e6a844ba1'
down_revision: Union[str, Sequence[str], None] = '40de804c9725'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inventory_type_enum = sa.Enum(InventoryType, name='inventorytype')
    inventory_type_enum.create(op.get_bind())
    
    op.add_column('inventory', sa.Column('type', inventory_type_enum, nullable=True))
    
    op.execute(f"UPDATE inventory SET type = 'THREAD' WHERE type IS NULL")
    op.alter_column('inventory', 'type', nullable=False)
    
    op.alter_column('inventory', 'price_per_kg',
        existing_type=sa.INTEGER(),
        type_=sa.Float(),
        nullable=True,
        existing_nullable=False,
        existing_server_default=sa.text("'0'"))
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('inventory', 'price_per_kg',
        existing_type=sa.Float(),
        type_=sa.INTEGER(),
        nullable=False,
        existing_nullable=True,
        existing_server_default=sa.text("'0'"))

    op.drop_column('inventory', 'type')

    inventory_type_enum = sa.Enum(InventoryType, name='inventorytype')
    inventory_type_enum.drop(op.get_bind())
