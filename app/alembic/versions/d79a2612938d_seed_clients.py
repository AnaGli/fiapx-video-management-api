"""seed clients

Revision ID: d79a2612938d
Revises: 5d052eab9a50
Create Date: 2026-01-17 18:56:30.450890

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'd79a2612938d'
down_revision: Union[str, Sequence[str], None] = '5d052eab9a50'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute(
        """
        INSERT INTO clients (name, cpf, email) VALUES
        ('João Silva', '71403108072', 'joao@email.com'),
        ('Maria Santos', '54182713001', 'maria@email.com'),
        ('Pedro Oliveira', '50560383002', 'pedro@email.com'),
        ('Ana Costa', '69010734021', 'ana@email.com');
        """
    )


def downgrade():
    op.execute(
        """
        DELETE FROM clients
        WHERE cpf IN (
            '71403108072',
            '54182713001',
            '50560383002',
            '69010734021'
        );
        """
    )