from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
import enum

from app.db.session import Base


class ReservationStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    RELEASED = "released"
    EXPIRED = "expired"


class Inventory(Base):
    __tablename__ = 'inventory'
    
    product_id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Integer, nullable=False, default=0)
    reserved_quantity = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    reservations = relationship("InventoryReservation", back_populates="inventory", cascade="all, delete-orphan", primaryjoin="Inventory.product_id==InventoryReservation.product_id", foreign_keys="InventoryReservation.product_id")
    
    @property
    def available_quantity(self) -> int:
        return self.quantity - self.reserved_quantity


class InventoryReservation(Base):
    __tablename__ = 'inventory_reservations'
    
    reservation_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('inventory.product_id', ondelete='CASCADE'), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    status = Column(SQLEnum(ReservationStatus), nullable=False, default=ReservationStatus.PENDING)
    order_id = Column(Integer, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    inventory = relationship("Inventory", back_populates="reservations")
