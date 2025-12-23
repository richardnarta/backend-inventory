"""streamlined inventory schema

Revision ID: a1b2c3d4e5f6
Revises: 
Create Date: 2025-12-23 10:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema - Create streamlined inventory system"""
    
    # --- Group 1: Core tables with no dependencies ---
    
    op.create_table('buyer',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('phone_num', sa.String(length=50), nullable=True),
        sa.Column('address', sa.String(), nullable=True),
        sa.Column('note', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_buyer_name'), 'buyer', ['name'], unique=False)
    
    op.create_table('supplier',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('phone_num', sa.String(length=50), nullable=True),
        sa.Column('address', sa.String(), nullable=True),
        sa.Column('note', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_supplier_name'), 'supplier', ['name'], unique=False)
    
    op.create_table('users',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('nama', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    
    # --- Group 2: Inventory table ---
    
    op.create_table('inventory',
        sa.Column('kode_barang', sa.String(), nullable=False),
        sa.Column('nama_barang', sa.String(), nullable=False),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('quantity_unit', sa.String(), nullable=False),
        sa.Column('harga_modal', sa.Float(), nullable=False),
        sa.Column('harga_jual_eceran', sa.Float(), nullable=False),
        sa.Column('harga_jual_grosir', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('kode_barang')
    )
    op.create_index(op.f('ix_inventory_nama_barang'), 'inventory', ['nama_barang'], unique=False)
    
    # --- Group 3: Tables with foreign key dependencies ---
    
    op.create_table('refresh_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_refresh_tokens_token'), 'refresh_tokens', ['token'], unique=True)
    
    op.create_table('purchase_transaction',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('transaction_date', sa.DateTime(), nullable=False),
        sa.Column('supplier_id', sa.Integer(), nullable=True),
        sa.Column('inventory_id', sa.String(), nullable=True),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('quantity_unit', sa.String(), nullable=False),
        sa.Column('price_per_unit', sa.Float(), nullable=False),
        sa.Column('total_price', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['inventory_id'], ['inventory.kode_barang'], ),
        sa.ForeignKeyConstraint(['supplier_id'], ['supplier.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_purchase_transaction_inventory_id'), 'purchase_transaction', ['inventory_id'], unique=False)
    op.create_index(op.f('ix_purchase_transaction_supplier_id'), 'purchase_transaction', ['supplier_id'], unique=False)
    op.create_index(op.f('ix_purchase_transaction_transaction_date'), 'purchase_transaction', ['transaction_date'], unique=False)
    
    op.create_table('sales_transaction',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('transaction_date', sa.DateTime(), nullable=False),
        sa.Column('buyer_id', sa.Integer(), nullable=True),
        sa.Column('inventory_id', sa.String(), nullable=True),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('quantity_unit', sa.String(), nullable=False),
        sa.Column('price_per_unit', sa.Float(), nullable=False),
        sa.Column('total_price', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['buyer_id'], ['buyer.id'], ),
        sa.ForeignKeyConstraint(['inventory_id'], ['inventory.kode_barang'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sales_transaction_buyer_id'), 'sales_transaction', ['buyer_id'], unique=False)
    op.create_index(op.f('ix_sales_transaction_inventory_id'), 'sales_transaction', ['inventory_id'], unique=False)
    op.create_index(op.f('ix_sales_transaction_transaction_date'), 'sales_transaction', ['transaction_date'], unique=False)


def downgrade() -> None:
    """Downgrade database schema - Drop all tables"""
    
    # Drop tables in reverse order of creation
    op.drop_index(op.f('ix_sales_transaction_transaction_date'), table_name='sales_transaction')
    op.drop_index(op.f('ix_sales_transaction_inventory_id'), table_name='sales_transaction')
    op.drop_index(op.f('ix_sales_transaction_buyer_id'), table_name='sales_transaction')
    op.drop_table('sales_transaction')
    
    op.drop_index(op.f('ix_purchase_transaction_transaction_date'), table_name='purchase_transaction')
    op.drop_index(op.f('ix_purchase_transaction_supplier_id'), table_name='purchase_transaction')
    op.drop_index(op.f('ix_purchase_transaction_inventory_id'), table_name='purchase_transaction')
    op.drop_table('purchase_transaction')
    
    op.drop_index(op.f('ix_refresh_tokens_token'), table_name='refresh_tokens')
    op.drop_table('refresh_tokens')
    
    op.drop_index(op.f('ix_inventory_nama_barang'), table_name='inventory')
    op.drop_table('inventory')
    
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    
    op.drop_index(op.f('ix_supplier_name'), table_name='supplier')
    op.drop_table('supplier')
    
    op.drop_index(op.f('ix_buyer_name'), table_name='buyer')
    op.drop_table('buyer')
