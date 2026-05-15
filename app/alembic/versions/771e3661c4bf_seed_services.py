"""seed services

Revision ID: 771e3661c4bf
Revises: af649ec1a6a7
Create Date: 2026-01-17 19:31:07.456962

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '771e3661c4bf'
down_revision: Union[str, Sequence[str], None] = 'af649ec1a6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute(
        """
        INSERT INTO services (name, description, price) VALUES
        ('Troca de óleo', 'Substituição do óleo do motor', 150.00),
        ('Alinhamento', 'Alinhamento e balanceamento das rodas', 120.00),
        ('Balanceamento', 'Balanceamento das rodas', 90.00),
        ('Troca de pastilhas de freio', 'Substituição das pastilhas de freio', 250.00);
        """
    )


def downgrade():
    op.execute(
        """
        DELETE FROM services
        WHERE name IN (
            'Troca de óleo',
            'Alinhamento',
            'Balanceamento',
            'Troca de pastilhas de freio'
        );
        """
    )