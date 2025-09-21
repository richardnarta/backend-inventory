"""create knitting process table

Revision ID: 4001f8134922
Revises: da0863cccae2
Create Date: 2025-09-21 14:23:13.967813

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4001f8134922'
down_revision: Union[str, Sequence[str], None] = 'da0863cccae2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('knitting_process',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('knit_formula_id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('weight_kg', sa.Float(), nullable=False),
    sa.Column('materials', sa.JSON(), nullable=False),
    sa.ForeignKeyConstraint(['knit_formula_id'], ['knit_formula.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_knitting_process_date'), 'knitting_process', ['date'], unique=False)
    op.create_index(op.f('ix_knitting_process_knit_formula_id'), 'knitting_process', ['knit_formula_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_knitting_process_knit_formula_id'), table_name='knitting_process')
    op.drop_index(op.f('ix_knitting_process_date'), table_name='knitting_process')
    op.drop_table('knitting_process')
