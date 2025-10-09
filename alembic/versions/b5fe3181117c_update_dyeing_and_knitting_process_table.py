"""update dyeing and knitting process table

Revision ID: b5fe3181117c
Revises: e13b653d5b2b
Create Date: 2025-10-09 11:08:14.291148

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b5fe3181117c'
down_revision: Union[str, Sequence[str], None] = 'e13b653d5b2b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_index(op.f('ix_dyeing_process_product_id'), table_name='dyeing_process')
    # Re-create it as a non-unique index since it's still used for lookups
    op.create_index(op.f('ix_dyeing_process_product_id'), 'dyeing_process', ['product_id'], unique=False)
    # Drop the explicit unique constraint from the table definition
    # The constraint name is often auto-generated; we assume a conventional name.
    # If this fails, check your DB for the actual constraint name.
    try:
        op.drop_constraint('dyeing_process_product_id_key', 'dyeing_process', type_='unique')
    except Exception:
        print("Constraint 'dyeing_process_product_id_key' not found, skipping drop.")


    # --- For knit_formula table ---
    # Drop the existing unique index first
    op.drop_index(op.f('ix_knit_formula_product_id'), table_name='knit_formula')
    # Re-create it as a non-unique index
    op.create_index(op.f('ix_knit_formula_product_id'), 'knit_formula', ['product_id'], unique=False)
    # Drop the explicit unique constraint
    try:
        op.drop_constraint('knit_formula_product_id_key', 'knit_formula', type_='unique')
    except Exception:
        print("Constraint 'knit_formula_product_id_key' not found, skipping drop.")
        
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_knit_formula_product_id'), table_name='knit_formula')
    # Re-create it as a unique index
    op.create_index(op.f('ix_knit_formula_product_id'), 'knit_formula', ['product_id'], unique=True)
    # Re-create the unique constraint
    op.create_unique_constraint('knit_formula_product_id_key', 'knit_formula', ['product_id'])

    # --- For dyeing_process table ---
    # Drop the non-unique index
    op.drop_index(op.f('ix_dyeing_process_product_id'), table_name='dyeing_process')
    # Re-create it as a unique index
    op.create_index(op.f('ix_dyeing_process_product_id'), 'dyeing_process', ['product_id'], unique=True)
    # Re-create the unique constraint
    op.create_unique_constraint('dyeing_process_product_id_key', 'dyeing_process', ['product_id'])

    # ### end Alembic commands ###
