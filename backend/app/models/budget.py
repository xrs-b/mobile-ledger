"""
预算模型
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, Text
from sqlalchemy.sql import func
from app.database import Base


class Budget(Base):
    """预算模型"""
    __tablename__ = "budgets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    category_id = Column(Integer, nullable=True)  # None表示总预算
    
    name = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    period = Column(String(20), default="monthly")  # monthly/yearly/custom
    
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    alert_threshold = Column(Float, default=80)  # 百分比
    
    is_active = Column(Boolean, default=True)
    description = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Budget {self.id}: {self.name} - {self.amount}>"
