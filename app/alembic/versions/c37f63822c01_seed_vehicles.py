"""seed vehicles

Revision ID: c37f63822c01
Revises: 9b5deaab1f5d
Create Date: 2026-01-17 19:14:27.262983

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'c37f63822c01'
down_revision: Union[str, Sequence[str], None] = '9b5deaab1f5d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute(
        """
        INSERT INTO vehicles (plate, brand, model, year, client_id)
        SELECT 'ABC1234', 'Toyota', 'Corolla', 2020, c.id
        FROM clients c
        WHERE c.cpf = '71403108072'
        AND NOT EXISTS (
            SELECT 1 FROM vehicles v WHERE v.plate = 'ABC1234'
        );

        INSERT INTO vehicles (plate, brand, model, year, client_id)
        SELECT 'DEF5678', 'Honda', 'Civic', 2019, c.id
        FROM clients c
        WHERE c.cpf = '54182713001'
        AND NOT EXISTS (
            SELECT 1 FROM vehicles v WHERE v.plate = 'DEF5678'
        );

        INSERT INTO vehicles (plate, brand, model, year, client_id)
        SELECT 'GHI9012', 'Volkswagen', 'Golf', 2021, c.id
        FROM clients c
        WHERE c.cpf = '71403108072'
        AND NOT EXISTS (
            SELECT 1 FROM vehicles v WHERE v.plate = 'GHI9012'
        );
        """
    )


def downgrade():
    op.execute(
        """
        DELETE FROM vehicles
        WHERE plate IN (
            'ABC1234',
            'DEF5678',
            'GHI9012'
        );
        """
    )