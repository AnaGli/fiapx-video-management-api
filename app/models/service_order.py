
from sqlalchemy import Enum, Numeric, ForeignKey, DateTime

from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from datetime import datetime

from app.database import Base

class ServiceOrderStatus(enum.Enum):
    RECEBIDA = "RECEBIDA"
    EM_DIAGNOSTICO = "EM_DIAGNOSTICO"
    AGUARDANDO_APROVACAO = "AGUARDANDO_APROVACAO"
    EM_EXECUCAO = "EM_EXECUCAO"
    FINALIZADA = "FINALIZADA"
    ENTREGUE = "ENTREGUE"

class ServiceOrder(Base):
    __tablename__ = "service_orders"

    id: Mapped[int] = mapped_column(primary_key=True)

    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id"), nullable=False
    )

    client = relationship("Client")

    vehicle_id: Mapped[int] = mapped_column(
        ForeignKey("vehicles.id"), nullable=False
    )

    status: Mapped[ServiceOrderStatus] = mapped_column(
    Enum(ServiceOrderStatus),
    default=ServiceOrderStatus.RECEBIDA,
    nullable=False,
)
    total_amount: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False, default=0
    )

    execution_started_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    execution_finished_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    items = relationship(
        "ServiceOrderItem",
        back_populates="service_order",
        cascade="all, delete-orphan",
    )
