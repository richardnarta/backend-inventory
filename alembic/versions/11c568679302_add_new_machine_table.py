"""add new machine table

Revision ID: 11c568679302
Revises: 275feadc8b6a
Create Date: 2025-09-20 20:20:31.059634

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '11c568679302'
down_revision: Union[str, Sequence[str], None] = '275feadc8b6a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('machine',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_machine_name'), 'machine', ['name'], unique=True)
    

    op.create_table('machine_activity',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('machine_id', sa.Integer(), nullable=False),
        sa.Column('inventory_id', sa.String(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('lot', sa.String(), nullable=False),
        sa.Column('operator', sa.String(), nullable=False),
        sa.Column('damaged_thread', sa.Float(), nullable=True),
        sa.Column('product_weight', sa.Float(), nullable=True),
        sa.Column('note', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['inventory_id'], ['inventory.id'], ),
        sa.ForeignKeyConstraint(['machine_id'], ['machine.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_machine_activity_date'), 'machine_activity', ['date'], unique=False)
    op.create_index(op.f('ix_machine_activity_inventory_id'), 'machine_activity', ['inventory_id'], unique=False)
    op.create_index(op.f('ix_machine_activity_machine_id'), 'machine_activity', ['machine_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_machine_activity_machine_id'), table_name='machine_activity')
    op.drop_index(op.f('ix_machine_activity_inventory_id'), table_name='machine_activity')
    op.drop_index(op.f('ix_machine_activity_date'), table_name='machine_activity')
    op.drop_table('machine_activity')
    
    op.drop_index(op.f('ix_machine_name'), table_name='machine')
    op.drop_table('machine')
