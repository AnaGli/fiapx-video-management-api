from sqlalchemy import String, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.database import Base


class ServiceOrderItem(Base):
    __tablename__ = "service_order_items"

    id: Mapped[int] = mapped_column(primary_key=True)

    service_order_id: Mapped[int] = mapped_column(
        ForeignKey("service_orders.id", ondelete="CASCADE"),
        nullable=False,
    )

    item_type: Mapped[str] = mapped_column(String(10), nullable=False)  # SERVICE | PART
    item_id: Mapped[int] = mapped_column(nullable=False)

    description: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(10, 3), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow
    )

    service_order = relationship(
        "ServiceOrder",
        back_populates="items",
    )
