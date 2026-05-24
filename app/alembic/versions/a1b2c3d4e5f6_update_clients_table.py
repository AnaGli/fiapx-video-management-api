"""add is_active column to clients table

Revision ID: a1b2c3d4e5f6
Revises: 5d052eab9a50
Create Date: 2026-05-22 19:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "de6295f16cf4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "clients",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true()
        )
    )


    op.execute(
        "UPDATE clients SET is_active = true"
    )


    op.alter_column(
        "clients",
        "is_active",
        server_default=None
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column("clients", "is_active")