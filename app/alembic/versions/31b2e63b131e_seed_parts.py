"""seed parts

Revision ID: 31b2e63b131e
Revises: aa0a285cf8f6
Create Date: 2026-01-17 20:04:25.316881

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '31b2e63b131e'
down_revision: Union[str, Sequence[str], None] = 'aa0a285cf8f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute(
        """
        INSERT INTO parts (name, description, unit, quantity, price, active)
        VALUES
        ('Óleo 5W30', 'Óleo sintético para motor', 'litro', 50, 45.90, true),
        ('Filtro de óleo', 'Filtro de óleo padrão', 'unidade', 30, 25.00, true),
        ('Pastilha de freio', 'Pastilha de freio dianteira', 'jogo', 20, 120.00, true),
        ('Fluido de freio', 'Fluido DOT 4', 'litro', 15, 35.00, true);
        """
    )


def downgrade():
    op.execute(
        """
        DELETE FROM parts
        WHERE name IN (
            'Óleo 5W30',
            'Filtro de óleo',
            'Pastilha de freio',
            'Fluido de freio'
        );
        """
    )