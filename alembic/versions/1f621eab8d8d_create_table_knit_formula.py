"""create table knit formula

Revision ID: 1f621eab8d8d
Revises: 11c568679302
Create Date: 2025-09-21 09:31:01.649939

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1f621eab8d8d'
down_revision: Union[str, Sequence[str], None] = '11c568679302'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('knit_formula',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.String(), nullable=False),
    sa.Column('formula', sa.JSON(), nullable=False),
    sa.ForeignKeyConstraint(['product_id'], ['inventory.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('product_id')
    )
    op.create_index(op.f('ix_knit_formula_product_id'), 'knit_formula', ['product_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_knit_formula_product_id'), table_name='knit_formula')
    op.drop_table('knit_formula')
