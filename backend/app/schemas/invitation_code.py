"""
邀请码Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class InvitationCodeCreate(BaseModel):
    """创建邀请码请求"""
    code: str = Field(..., min_length=4, max_length=20, description="邀请码")
    valid_days: Optional[int] = Field(None, ge=1, le=365, description="有效天数")


class InvitationCodeResponse(BaseModel):
    """邀请码响应"""
    id: int
    code: str
    is_used: bool
    expires_at: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


class InvitationCodeListResponse(BaseModel):
    """邀请码列表响应"""
    total: int
    codes: List[dict]
