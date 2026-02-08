"""add_multi_item_transaction_support

Revision ID: 1c3e15b4ac48
Revises: db89ee4d61ca
Create Date: 2026-02-08 14:44:57.479161

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1c3e15b4ac48'
down_revision: Union[str, Sequence[str], None] = 'db89ee4d61ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Transform single-item transaction tables to multi-item header-detail pattern.
    
    Steps:
    1. Create temporary backup of existing data
    2. Create new item tables
    3. Migrate existing transaction data to item tables
    4. Modify existing tables to become headers
    """
    
    # ===== PURCHASE TRANSACTION MIGRATION =====
    
    # Step 1: Create temporary table to backup existing purchase transactions
    op.execute("""
        CREATE TEMPORARY TABLE temp_purchase_backup AS 
        SELECT * FROM purchase_transaction
    """)
    
    # Step 2: Create new purchase_transaction_item table
    op.create_table(
        'purchase_transaction_item',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('purchase_transaction_id', sa.Integer(), nullable=False),
        sa.Column('inventory_id', sa.String(), nullable=True),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('quantity_unit', sa.String(), nullable=False),
        sa.Column('price_per_unit', sa.Float(), nullable=False),
        sa.Column('subtotal', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['inventory_id'], ['inventory.kode_barang'], ),
        sa.ForeignKeyConstraint(['purchase_transaction_id'], ['purchase_transaction.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        'ix_purchase_transaction_item_purchase_transaction_id', 
        'purchase_transaction_item', 
        ['purchase_transaction_id']
    )
    op.create_index(
        'ix_purchase_transaction_item_inventory_id', 
        'purchase_transaction_item', 
        ['inventory_id']
    )
    
    # Step 3: Migrate existing data to item table
    # Each old transaction becomes 1 header + 1 item
    op.execute("""
        INSERT INTO purchase_transaction_item 
            (purchase_transaction_id, inventory_id, quantity, quantity_unit, price_per_unit, subtotal)
        SELECT 
            id,
            inventory_id,
            quantity,
            quantity_unit,
            price_per_unit,
            total_price
        FROM temp_purchase_backup
    """)
    
    # Step 4: Modify purchase_transaction table to become header
    # Drop item-specific columns
    op.drop_constraint('purchase_transaction_inventory_id_fkey', 'purchase_transaction', type_='foreignkey')
    op.drop_index('ix_purchase_transaction_inventory_id', table_name='purchase_transaction')
    op.drop_column('purchase_transaction', 'inventory_id')
    op.drop_column('purchase_transaction', 'quantity')
    op.drop_column('purchase_transaction', 'quantity_unit')
    op.drop_column('purchase_transaction', 'price_per_unit')
    op.drop_column('purchase_transaction', 'total_price')
    
    # Add header-specific columns
    op.add_column('purchase_transaction', sa.Column('notes', sa.Text(), nullable=True))
    op.add_column('purchase_transaction', sa.Column('total_amount', sa.Float(), nullable=False, server_default='0'))
    
    # Update total_amount from migrated items
    op.execute("""
        UPDATE purchase_transaction pt
        SET total_amount = (
            SELECT COALESCE(SUM(subtotal), 0)
            FROM purchase_transaction_item pti
            WHERE pti.purchase_transaction_id = pt.id
        )
    """)
    
    # ===== SALES TRANSACTION MIGRATION =====
    
    # Step 1: Create temporary table to backup existing sales transactions
    op.execute("""
        CREATE TEMPORARY TABLE temp_sales_backup AS 
        SELECT * FROM sales_transaction
    """)
    
    # Step 2: Create new sales_transaction_item table
    op.create_table(
        'sales_transaction_item',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sales_transaction_id', sa.Integer(), nullable=False),
        sa.Column('inventory_id', sa.String(), nullable=True),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('quantity_unit', sa.String(), nullable=False),
        sa.Column('price_per_unit', sa.Float(), nullable=False),
        sa.Column('subtotal', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['inventory_id'], ['inventory.kode_barang'], ),
        sa.ForeignKeyConstraint(['sales_transaction_id'], ['sales_transaction.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        'ix_sales_transaction_item_sales_transaction_id', 
        'sales_transaction_item', 
        ['sales_transaction_id']
    )
    op.create_index(
        'ix_sales_transaction_item_inventory_id', 
        'sales_transaction_item', 
        ['inventory_id']
    )
    
    # Step 3: Migrate existing data to item table
    op.execute("""
        INSERT INTO sales_transaction_item 
            (sales_transaction_id, inventory_id, quantity, quantity_unit, price_per_unit, subtotal)
        SELECT 
            id,
            inventory_id,
            quantity,
            quantity_unit,
            price_per_unit,
            total_price
        FROM temp_sales_backup
    """)
    
    # Step 4: Modify sales_transaction table to become header
    # Drop item-specific columns
    op.drop_constraint('sales_transaction_inventory_id_fkey', 'sales_transaction', type_='foreignkey')
    op.drop_index('ix_sales_transaction_inventory_id', table_name='sales_transaction')
    op.drop_column('sales_transaction', 'inventory_id')
    op.drop_column('sales_transaction', 'quantity')
    op.drop_column('sales_transaction', 'quantity_unit')
    op.drop_column('sales_transaction', 'price_per_unit')
    op.drop_column('sales_transaction', 'total_price')
    
    # Add header-specific columns
    op.add_column('sales_transaction', sa.Column('notes', sa.Text(), nullable=True))
    op.add_column('sales_transaction', sa.Column('total_amount', sa.Float(), nullable=False, server_default='0'))
    
    # Update total_amount from migrated items
    op.execute("""
        UPDATE sales_transaction st
        SET total_amount = (
            SELECT COALESCE(SUM(subtotal), 0)
            FROM sales_transaction_item sti
            WHERE sti.sales_transaction_id = st.id
        )
    """)


def downgrade() -> None:
    """
    Revert multi-item transaction schema back to single-item.
    
    WARNING: This will only restore the first item of each transaction if there are multiple items.
    Data loss may occur if transactions have more than 1 item.
    """
    
    # ===== PURCHASE TRANSACTION ROLLBACK =====
    
    # Step 1: Add back item-specific columns
    op.add_column('purchase_transaction', sa.Column('inventory_id', sa.String(), nullable=True))
    op.add_column('purchase_transaction', sa.Column('quantity', sa.Float(), nullable=False, server_default='0'))
    op.add_column('purchase_transaction', sa.Column('quantity_unit', sa.String(), nullable=False, server_default=''))
    op.add_column('purchase_transaction', sa.Column('price_per_unit', sa.Float(), nullable=False, server_default='0'))
    op.add_column('purchase_transaction', sa.Column('total_price', sa.Float(), nullable=False, server_default='0'))
    
    # Step 2: Restore data from item table (only first item per transaction)
    op.execute("""
        UPDATE purchase_transaction pt
        SET 
            inventory_id = pti.inventory_id,
            quantity = pti.quantity,
            quantity_unit = pti.quantity_unit,
            price_per_unit = pti.price_per_unit,
            total_price = pti.subtotal
        FROM (
            SELECT DISTINCT ON (purchase_transaction_id) *
            FROM purchase_transaction_item
            ORDER BY purchase_transaction_id, id
        ) pti
        WHERE pt.id = pti.purchase_transaction_id
    """)
    
    # Step 3: Drop header-specific columns
    op.drop_column('purchase_transaction', 'total_amount')
    op.drop_column('purchase_transaction', 'notes')
    
    # Step 4: Re-add foreign key and index
    op.create_index('ix_purchase_transaction_inventory_id', 'purchase_transaction', ['inventory_id'])
    op.create_foreign_key(
        'purchase_transaction_inventory_id_fkey', 
        'purchase_transaction', 
        'inventory', 
        ['inventory_id'], 
        ['kode_barang']
    )
    
    # Step 5: Drop item table
    op.drop_index('ix_purchase_transaction_item_inventory_id', table_name='purchase_transaction_item')
    op.drop_index('ix_purchase_transaction_item_purchase_transaction_id', table_name='purchase_transaction_item')
    op.drop_table('purchase_transaction_item')
    
    # ===== SALES TRANSACTION ROLLBACK =====
    
    # Step 1: Add back item-specific columns
    op.add_column('sales_transaction', sa.Column('inventory_id', sa.String(), nullable=True))
    op.add_column('sales_transaction', sa.Column('quantity', sa.Float(), nullable=False, server_default='0'))
    op.add_column('sales_transaction', sa.Column('quantity_unit', sa.String(), nullable=False, server_default=''))
    op.add_column('sales_transaction', sa.Column('price_per_unit', sa.Float(), nullable=False, server_default='0'))
    op.add_column('sales_transaction', sa.Column('total_price', sa.Float(), nullable=False, server_default='0'))
    
    # Step 2: Restore data from item table (only first item per transaction)
    op.execute("""
        UPDATE sales_transaction st
        SET 
            inventory_id = sti.inventory_id,
            quantity = sti.quantity,
            quantity_unit = sti.quantity_unit,
            price_per_unit = sti.price_per_unit,
            total_price = sti.subtotal
        FROM (
            SELECT DISTINCT ON (sales_transaction_id) *
            FROM sales_transaction_item
            ORDER BY sales_transaction_id, id
        ) sti
        WHERE st.id = sti.sales_transaction_id
    """)
    
    # Step 3: Drop header-specific columns
    op.drop_column('sales_transaction', 'total_amount')
    op.drop_column('sales_transaction', 'notes')
    
    # Step 4: Re-add foreign key and index
    op.create_index('ix_sales_transaction_inventory_id', 'sales_transaction', ['inventory_id'])
    op.create_foreign_key(
        'sales_transaction_inventory_id_fkey', 
        'sales_transaction', 
        'inventory', 
        ['inventory_id'], 
        ['kode_barang']
    )
    
    # Step 5: Drop item table
    op.drop_index('ix_sales_transaction_item_inventory_id', table_name='sales_transaction_item')
    op.drop_index('ix_sales_transaction_item_sales_transaction_id', table_name='sales_transaction_item')
    op.drop_table('sales_transaction_item')

