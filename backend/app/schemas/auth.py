"""
认证请求/响应模型
"""
from pydantic import BaseModel, Field
from typing import Optional


# ============ Request Models ============

class RegisterRequest(BaseModel):
    """注册请求"""
    username: str = Field(..., min_length=4, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=128, description="密码")
    invitation_code: str = Field(..., description="邀请码")


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


# ============ Response Models ============

class RegisterResponse(BaseModel):
    """注册响应"""
    access_token: Optional[str] = None
    token_type: str = "bearer"
    user_id: int
    username: str
    is_admin: bool
    message: str


class LoginResponse(BaseModel):
    """登录响应"""
    token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class TokenPayload(BaseModel):
    """Token信息"""
    user_id: int
    username: str
    is_admin: bool
    exp: int


# ============ User Response Models ============

class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    is_admin: bool
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """用户列表响应"""
    total: int
    users: List[UserResponse]
