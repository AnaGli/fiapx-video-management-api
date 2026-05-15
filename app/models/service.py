from sqlalchemy import String, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class Service(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String(255))
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
