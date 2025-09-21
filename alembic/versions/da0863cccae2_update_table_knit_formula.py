"""update table knit formula

Revision ID: da0863cccae2
Revises: 1f621eab8d8d
Create Date: 2025-09-21 11:16:56.521505

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'da0863cccae2'
down_revision: Union[str, Sequence[str], None] = '1f621eab8d8d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('knit_formula', sa.Column(
        'production_weight', 
        sa.Float(), 
        nullable=False, 
        server_default=sa.text('0.0'))
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('knit_formula', 'production_weight')
