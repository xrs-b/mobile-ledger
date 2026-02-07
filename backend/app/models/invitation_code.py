"""
邀请码模型
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class InvitationCode(Base):
    """邀请码表"""
    __tablename__ = "invitation_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    is_used = Column(Boolean, default=False)
    used_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    used_at = Column(DateTime, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    used_by_user = relationship("User", foreign_keys=[used_by])
    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<InvitationCode(code='{self.code}', is_used={self.is_used})>"
