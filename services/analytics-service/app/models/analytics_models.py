from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, Numeric, Date

from app.db.session import Base


class DailySalesMetric(Base):
    __tablename__ = 'daily_sales_metrics'
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, unique=True, index=True)
    revenue = Column(Numeric(12, 2), nullable=False, default=0)
    orders_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class OrderStatusMetric(Base):
    __tablename__ = 'order_status_metrics'
    
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String(50), nullable=False, unique=True, index=True)
    count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class ProductMetric(Base):
    __tablename__ = 'product_metrics'
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, nullable=False, unique=True, index=True)
    product_name = Column(String(255), nullable=False)
    units_sold = Column(Integer, nullable=False, default=0)
    revenue = Column(Numeric(12, 2), nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class UserMetric(Base):
    __tablename__ = 'user_metrics'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False)
    last_active = Column(DateTime, nullable=True)
    created_at_record = Column(DateTime, default=datetime.utcnow, nullable=False)
