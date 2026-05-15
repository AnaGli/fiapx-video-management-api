"""seed users

Revision ID: 5ee036446a76
Revises: f493fdc7dd81
Create Date: 2026-01-17 20:44:04.293332

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5ee036446a76'
down_revision: Union[str, Sequence[str], None] = 'f493fdc7dd81'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute(
        """
        INSERT INTO users (username, password_hash, is_active)
        VALUES (
            'admin',
            '$2b$12$noc956SU310VT.BcmyQdlOYPVIYL0xtieK10rItM2ochLAofjlyNq',
            true
        );
        """
    )


def downgrade():
    op.execute(
        """
        DELETE FROM users
        WHERE username = 'admin';
        """
    )