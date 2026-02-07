"""
记账记录模型
"""
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.database import Base


class LedgerRecord(Base):
    """记账记录表"""
    __tablename__ = "ledger_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    type = Column(String(10), nullable=False)  # income/expense
    remark = Column(String(500), nullable=True)  # 备注
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)
    record_date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = relationship("User", backref="ledger_records")
    category = relationship("Category", backref="ledger_records")
    project = relationship("Project", backref="ledger_records")

    def __repr__(self):
        return f"<LedgerRecord(id={self.id}, amount={self.amount}, type='{self.type}')>"
