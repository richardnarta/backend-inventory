"""add_additional_note_and_update_quantity_units

Revision ID: db89ee4d61ca
Revises: a1b2c3d4e5f6
Create Date: 2026-01-11 20:38:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'db89ee4d61ca'
down_revision: Union[str, None] = '1827b6df991f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add additional_note column to inventory table
    op.add_column('inventory', sa.Column('additional_note', sa.String(), nullable=False, server_default=''))
    
    # Note: The quantity_unit column already exists as VARCHAR
    # We don't need to modify the column type, just update the constraint or validation
    # Since we're using pydantic validators in the schema, no database changes needed for enum values
    
    # Optional: If you want to update existing data to use new unit names, you can add update statements here
    # For example (uncomment and modify as needed):
    # op.execute("UPDATE inventory SET quantity_unit = 'Pcs' WHERE quantity_unit = 'buah'")
    # op.execute("UPDATE inventory SET quantity_unit = 'Dus' WHERE quantity_unit = 'dus'")
    # op.execute("UPDATE inventory SET quantity_unit = 'Bal' WHERE quantity_unit = 'bal'")
    # op.execute("UPDATE sales_transaction SET quantity_unit = 'Pcs' WHERE quantity_unit = 'buah'")
    # op.execute("UPDATE sales_transaction SET quantity_unit = 'Dus' WHERE quantity_unit = 'dus'")
    # op.execute("UPDATE sales_transaction SET quantity_unit = 'Bal' WHERE quantity_unit = 'bal'")
    # op.execute("UPDATE purchase_transaction SET quantity_unit = 'Pcs' WHERE quantity_unit = 'buah'")
    # op.execute("UPDATE purchase_transaction SET quantity_unit = 'Dus' WHERE quantity_unit = 'dus'")
    # op.execute("UPDATE purchase_transaction SET quantity_unit = 'Bal' WHERE quantity_unit = 'bal'")


def downgrade() -> None:
    # Remove additional_note column from inventory table
    op.drop_column('inventory', 'additional_note')
    
    # Optional: Revert unit name changes if you applied them in upgrade (uncomment if used above)
    # op.execute("UPDATE inventory SET quantity_unit = 'buah' WHERE quantity_unit = 'Pcs'")
    # op.execute("UPDATE inventory SET quantity_unit = 'dus' WHERE quantity_unit = 'Dus'")
    # op.execute("UPDATE inventory SET quantity_unit = 'bal' WHERE quantity_unit = 'Bal'")
    # op.execute("UPDATE sales_transaction SET quantity_unit = 'buah' WHERE quantity_unit = 'Pcs'")
    # op.execute("UPDATE sales_transaction SET quantity_unit = 'dus' WHERE quantity_unit = 'Dus'")
    # op.execute("UPDATE sales_transaction SET quantity_unit = 'bal' WHERE quantity_unit = 'Bal'")
    # op.execute("UPDATE purchase_transaction SET quantity_unit = 'buah' WHERE quantity_unit = 'Pcs'")
    # op.execute("UPDATE purchase_transaction SET quantity_unit = 'dus' WHERE quantity_unit = 'Dus'")
    # op.execute("UPDATE purchase_transaction SET quantity_unit = 'bal' WHERE quantity_unit = 'Bal'")
