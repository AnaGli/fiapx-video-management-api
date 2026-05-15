"""seed service orders

Revision ID: de6295f16cf4
Revises: b51881dba64a
Create Date: 2026-01-18 17:53:18.068951

"""
from datetime import datetime, timedelta
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'de6295f16cf4'
down_revision: Union[str, Sequence[str], None] = 'b51881dba64a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    conn = op.get_bind()
    now = datetime.utcnow()

    # =========================
    # OS 1 — RECEBIDA
    # =========================
    conn.execute(
        sa.text("""
            INSERT INTO service_orders
            (client_id, vehicle_id, status, total_amount, created_at, updated_at)
            VALUES (1, 1, 'RECEBIDA', 0, :now, :now)
            RETURNING id
        """),
        {"now": now},
    ).scalar()

    # =========================
    # OS 2 — AGUARDANDO_APROVACAO
    # =========================
    os2_id = conn.execute(
        sa.text("""
            INSERT INTO service_orders
            (client_id, vehicle_id, status, total_amount, created_at, updated_at)
            VALUES (2, 2, 'AGUARDANDO_APROVACAO', 333.60, :now, :now)
            RETURNING id
        """),
        {"now": now},
    ).scalar()

    conn.execute(
        sa.text("""
            INSERT INTO service_order_items
            (service_order_id, item_type, item_id, description, quantity, price, created_at)
            VALUES
            (:os_id, 'SERVICE', 1, 'Troca de óleo', 1, 150.00, :now),
            (:os_id, 'PART', 1, 'Óleo 5W30', 4, 45.90, :now)
        """),
        {"os_id": os2_id, "now": now},
    )

    # =========================
    # OS 3 — EM_EXECUCAO
    # =========================
    started_at = now - timedelta(hours=2)

    os3_id = conn.execute(
        sa.text("""
            INSERT INTO service_orders
            (client_id, vehicle_id, status, total_amount,
             execution_started_at, created_at, updated_at)
            VALUES
            (3, 3, 'EM_EXECUCAO', 120.00,
             :started_at, :now, :now)
            RETURNING id
        """),
        {"started_at": started_at, "now": now},
    ).scalar()

    conn.execute(
        sa.text("""
            INSERT INTO service_order_items
            (service_order_id, item_type, item_id, description, quantity, price, created_at)
            VALUES
            (:os_id, 'SERVICE', 2, 'Alinhamento', 1, 120.00, :now)
        """),
        {"os_id": os3_id, "now": now},
    )

    # =========================
    # OS 4 — FINALIZADA
    # =========================
    finished_at = now - timedelta(minutes=30)
    started_at = finished_at - timedelta(hours=3)

    os4_id = conn.execute(
        sa.text("""
            INSERT INTO service_orders
            (client_id, vehicle_id, status, total_amount,
             execution_started_at, execution_finished_at,
             created_at, updated_at)
            VALUES
            (1, 2, 'FINALIZADA', 420.00,
             :started_at, :finished_at,
             :now, :now)
            RETURNING id
        """),
        {
            "started_at": started_at,
            "finished_at": finished_at,
            "now": now,
        },
    ).scalar()

    conn.execute(
        sa.text("""
            INSERT INTO service_order_items
            (service_order_id, item_type, item_id, description, quantity, price, created_at)
            VALUES
            (:os_id, 'SERVICE', 3, 'Balanceamento', 1, 90.00, :now),
            (:os_id, 'PART', 2, 'Filtro de óleo', 1, 30.00, :now),
            (:os_id, 'PART', 1, 'Óleo 5W30', 3, 100.00, :now)
        """),
        {"os_id": os4_id, "now": now},
    )


def downgrade():
    op.execute("""
        DELETE FROM service_order_items
        WHERE service_order_id IN (
            SELECT id FROM service_orders
            WHERE status IN (
                'RECEBIDA',
                'AGUARDANDO_APROVACAO',
                'EM_EXECUCAO',
                'FINALIZADA'
            )
        )
    """)

    op.execute("""
        DELETE FROM service_orders
        WHERE status IN (
            'RECEBIDA',
            'AGUARDANDO_APROVACAO',
            'EM_EXECUCAO',
            'FINALIZADA'
        )
    """)