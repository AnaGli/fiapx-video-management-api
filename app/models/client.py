from sqlalchemy import String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    cpf: Mapped[str] = mapped_column(String(11), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    vehicles = relationship(
        "Vehicle",
        back_populates="client",
        cascade="all, delete-orphan",
    )
