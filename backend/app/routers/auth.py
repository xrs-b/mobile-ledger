"""
认证路由
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import User, InvitationCode, SystemConfig
from app.auth.password import hash_password, verify_password
from app.auth.token import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.auth.dependencies import get_current_user
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    RegisterResponse,
    LoginResponse,
)


router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=RegisterResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """用户注册"""
    # 1. 验证邀请码
    invitation = db.query(InvitationCode).filter(
        InvitationCode.code == request.invitation_code,
        InvitationCode.is_used == False
    ).first()
    
    if not invitation:
        # 检查是否是默认邀请码
        default_config = db.query(SystemConfig).filter(
            SystemConfig.config_key == "default_invitation_code"
        ).first()
        
        if not default_config or default_config.config_value != request.invitation_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邀请码无效"
            )
    
    # 2. 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 3. 创建用户
    hashed_password = hash_password(request.password)
    
    # 检查是否是第一个用户（第一个用户为管理员）
    user_count = db.query(func.count(User.id)).scalar()
    is_admin = (user_count == 0)
    
    user = User(
        username=request.username,
        password_hash=hashed_password,
        is_admin=is_admin,
        invitation_code=request.invitation_code
    )
    db.add(user)
    db.flush()  # 获取用户ID
    
    # 4. 标记邀请码已使用
    if invitation:
        invitation.is_used = True
        invitation.used_by = user.id
        invitation.used_at = func.now()
    
    db.commit()
    
    return RegisterResponse(
        user_id=user.id,
        username=user.username,
        is_admin=user.is_admin,
        message="注册成功"
    )


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    # 1. 查找用户
    user = db.query(User).filter(User.username == request.username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 2. 验证密码
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 3. 检查用户状态
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用"
        )
    
    # 4. 生成Token
    token_data = {
        "sub": user.id,
        "username": user.username,
        "is_admin": user.is_admin
    }
    token = create_access_token(token_data)
    
    return LoginResponse(
        token=token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={
            "id": user.id,
            "username": user.username,
            "is_admin": user.is_admin
        }
    )


@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "is_admin": current_user.is_admin,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at.isoformat()
    }
