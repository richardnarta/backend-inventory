"""create table supplier

Revision ID: 6110e2384212
Revises: 818e6a844ba1
Create Date: 2025-09-20 13:43:07.216908

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6110e2384212'
down_revision: Union[str, Sequence[str], None] = '818e6a844ba1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('supplier',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('phone_num', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_supplier_name'), 'supplier', ['name'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_supplier_name'), table_name='supplier')
    op.drop_table('supplier')
