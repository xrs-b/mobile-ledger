"""
分类模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Category(Base):
    """分类表（一级+二级）"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    # nullable=True表示系统默认分类
    name = Column(String(100), nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)
    icon = Column(String(255), nullable=True)  # 图标URL或emoji
    type = Column(String(10), nullable=False)  # income/expense
    is_system = Column(Boolean, default=False)  # 是否系统分类
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    parent = relationship("Category", remote_side=[id], backref="children")
    user = relationship("User", backref="categories")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', type='{self.type}')>"
