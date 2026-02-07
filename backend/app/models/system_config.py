"""
系统配置模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from app.database import Base


class SystemConfig(Base):
    """系统配置表"""
    __tablename__ = "system_config"

    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(100), unique=True, nullable=False, index=True)
    config_value = Column(Text, nullable=True)
    description = Column(String(500), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<SystemConfig(key='{self.config_key}', value='{self.config_value}')>"
