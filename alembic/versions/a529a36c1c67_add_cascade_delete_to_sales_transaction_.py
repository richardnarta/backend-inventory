"""Add cascade delete to sales transaction relationships

Revision ID: a529a36c1c67
Revises: a6343b73b898
Create Date: 2025-08-24 09:38:21.308291

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a529a36c1c67'
down_revision: Union[str, Sequence[str], None] = 'a6343b73b898'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Applies the cascade delete functionality to the foreign keys.
    """
    # Note: You may need to find the exact constraint names from your database.
    # You can find them by connecting to psql and running: \d sales_transaction
    
    # Drop the existing foreign key constraints first
    try:
        op.drop_constraint(
            'sales_transaction_buyer_id_fkey',
            'sales_transaction', 
            type_='foreignkey'
        )
        op.drop_constraint(
            'sales_transaction_inventory_id_fkey',
            'sales_transaction', 
            type_='foreignkey'
        )
        op.drop_constraint(
            'account_receivable_buyer_id_fkey',
            'account_receivable', 
            type_='foreignkey'
        )
    except Exception as e:
        print(f"Could not drop constraints, they might not exist or have different names. Error: {e}")


    # Re-create the foreign key constraints with ON DELETE CASCADE
    op.create_foreign_key(
        'fk_sales_transaction_buyer_id',  # New, more explicit constraint name
        'sales_transaction', 'buyer',
        ['buyer_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_sales_transaction_inventory_id', # New, more explicit constraint name
        'sales_transaction', 'inventory',
        ['inventory_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_account_receivable_buyer_id', # New, more explicit constraint name
        'account_receivable', 'buyer',
        ['buyer_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    """
    Reverts the changes, removing the cascade delete functionality.
    """
    # Drop the CASCADE constraints
    op.drop_constraint(
        'fk_sales_transaction_inventory_id',
        'sales_transaction', 
        type_='foreignkey'
    )
    op.drop_constraint(
        'fk_sales_transaction_buyer_id',
        'sales_transaction', 
        type_='foreignkey'
    )
    op.drop_constraint(
        'fk_account_receivable_buyer_id',
        'account_receivable', 
        type_='foreignkey'
    )

    # Re-create the old constraints without CASCADE
    op.create_foreign_key(
        'sales_transaction_inventory_id_fkey',
        'sales_transaction', 'inventory',
        ['inventory_id'], ['id']
    )
    op.create_foreign_key(
        'sales_transaction_buyer_id_fkey',
        'sales_transaction', 'buyer',
        ['buyer_id'], ['id']
    )
    op.create_foreign_key(
        'account_receivable_buyer_id_fkey',
        'saccount_receivable', 'buyer',
        ['buyer_id'], ['id']
    )
