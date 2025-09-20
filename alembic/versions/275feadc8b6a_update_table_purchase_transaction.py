"""update table purchase

Revision ID: 275feadc8b6a
Revises: 2050b14c3f29
Create Date: 2025-09-20 18:27:45.523253

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '275feadc8b6a'
down_revision: Union[str, Sequence[str], None] = '2050b14c3f29'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('purchase_transaction', sa.Column('dye_overhead_cost', sa.Float(), nullable=True))
    op.add_column('purchase_transaction', sa.Column('dye_final_weight', sa.Float(), nullable=True))
    op.add_column('purchase_transaction', sa.Column('dye_price_per_kg', sa.Float(), nullable=True))
    op.add_column('purchase_transaction', sa.Column('dye_status', sa.Boolean(), server_default=sa.false(), nullable=False))
    
    # Step 2: Create an index on the new status column
    op.create_index(op.f('ix_purchase_transaction_dye_status'), 'purchase_transaction', ['dye_status'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_purchase_transaction_dye_status'), table_name='purchase_transaction')
    
    # Step 3: Drop the columns from purchase_transaction
    op.drop_column('purchase_transaction', 'dye_status')
    op.drop_column('purchase_transaction', 'dye_price_per_kg')
    op.drop_column('purchase_transaction', 'dye_final_weight')
    op.drop_column('purchase_transaction', 'dye_overhead_cost')
