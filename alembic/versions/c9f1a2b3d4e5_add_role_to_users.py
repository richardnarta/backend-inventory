"""add role to users table

Revision ID: c9f1a2b3d4e5
Revises: 1827b6df991f
Create Date: 2026-02-24 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c9f1a2b3d4e5'
down_revision: Union[str, Sequence[str], None] = '1c3e15b4ac48'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Define the enum type
userrole_enum = sa.Enum('root', 'admin', 'staff', name='userrole')


def upgrade() -> None:
    """Add role column to users table and set existing users' roles."""

    # Create the enum type in PostgreSQL
    userrole_enum.create(op.get_bind(), checkfirst=True)

    # Add the role column with default 'staff'
    op.add_column(
        'users',
        sa.Column(
            'role',
            sa.Enum('root', 'admin', 'staff', name='userrole'),
            nullable=False,
            server_default='staff'
        )
    )

    # Update the root user to have role 'root'
    op.execute("UPDATE users SET role = 'root' WHERE username = 'root'")


def downgrade() -> None:
    """Remove role column from users table."""
    op.drop_column('users', 'role')
    userrole_enum.drop(op.get_bind(), checkfirst=True)
