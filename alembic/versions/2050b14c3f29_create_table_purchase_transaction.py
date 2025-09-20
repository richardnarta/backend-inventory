"""create table purchase transaction

Revision ID: 2050b14c3f29
Revises: 6110e2384212
Create Date: 2025-09-20 14:44:33.487098

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2050b14c3f29'
down_revision: Union[str, Sequence[str], None] = '6110e2384212'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('purchase_transaction',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('transaction_date', sa.DateTime(), nullable=False),
    sa.Column('supplier_id', sa.Integer(), nullable=False),
    sa.Column('inventory_id', sa.String(length=50), nullable=False),
    sa.Column('roll_count', sa.Float(), nullable=True),
    sa.Column('weight_kg', sa.Float(), nullable=True),
    sa.Column('price_per_kg', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['supplier_id'], ['supplier.id'], ),
    sa.ForeignKeyConstraint(['inventory_id'], ['inventory.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_purchase_transaction_supplier_id'), 'purchase_transaction', ['supplier_id'], unique=False)
    op.create_index(op.f('ix_purchase_transaction_inventory_id'), 'purchase_transaction', ['inventory_id'], unique=False)
    op.create_index(op.f('ix_purchase_transaction_transaction_date'), 'purchase_transaction', ['transaction_date'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_purchase_transaction_transaction_date'), table_name='purchase_transaction')
    op.drop_index(op.f('ix_purchase_transaction_inventory_id'), table_name='purchase_transaction')
    op.drop_index(op.f('ix_purchase_transaction_supplier_id'), table_name='purchase_transaction')
    op.drop_table('purchase_transaction')
