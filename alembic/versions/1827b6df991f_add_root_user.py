"""add root user

Revision ID: 1827b6df991f
Revises: e13b653d5b2b
Create Date: 2025-10-17 00:29:04.573030

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1827b6df991f'
down_revision: Union[str, Sequence[str], None] = 'e13b653d5b2b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ROOT_USER_DATA = {
    "id": uuid.uuid4(),
    "nama": "Julius",
    "username": "root",
    "hashed_password": "$2b$12$XWii8V97mSUS9srYUzrgoeR5fcAFvJqcxBcHTR5OiZL7ehOMCu8Hu",
}

def upgrade() -> None:
    """Upgrade schema."""
    users_table = sa.table(
        "users",
        sa.column("id", sa.Uuid), # Menggunakan sa.String agar kompatibel dengan UUID sebagai string
        sa.column("nama", sa.String),
        sa.column("username", sa.String),
        sa.column("hashed_password", sa.String),
    )

    # Memasukkan data pengguna root ke dalam tabel
    op.bulk_insert(
        users_table,
        [
            ROOT_USER_DATA
        ],
    )


def downgrade() -> None:
    """
    Membatalkan migrasi dengan menghapus pengguna 'root'.
    """
    op.execute(
        f"DELETE FROM users WHERE username = '{ROOT_USER_DATA['username']}'"
    )
