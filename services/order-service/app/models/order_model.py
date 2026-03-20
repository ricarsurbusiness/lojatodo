from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, Numeric, Enum as SQLEnum, String
from sqlalchemy.orm import relationship
import enum

from app.db.session import Base


class OrderStatus(str, enum.Enum):
    PENDING = "pendiente"
    CONFIRMED = "confirmado"
    SHIPPED = "enviado"
    DELIVERED = "entregado"
    FAILED = "fallido"
    CANCELLED = "cancelado"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    status = Column(SQLEnum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    total_amount = Column(Numeric(10, 2), nullable=False)
    shipping_street = Column(String(120), nullable=False)
    shipping_city = Column(String(80), nullable=False)
    shipping_state = Column(String(80), nullable=False)
    shipping_zip_code = Column(String(20), nullable=False)
    shipping_country = Column(String(80), nullable=False)
    payment_id = Column(Integer, nullable=True, index=True)
    tracking_number = Column(String(100), nullable=True)
    carrier = Column(String(80), nullable=True)
    estimated_delivery = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
