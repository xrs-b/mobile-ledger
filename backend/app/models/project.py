"""
项目模型
"""
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.database import Base


class Project(Base):
    """项目表"""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=True)
    budget = Column(Numeric(12, 2), default=0)
    member_count = Column(Integer, default=1)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    status = Column(String(20), default="active")  # active/completed/cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = relationship("User", backref="projects")

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', budget={self.budget})>"
