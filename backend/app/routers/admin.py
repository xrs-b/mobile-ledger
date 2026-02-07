"""
用户管理路由 - 仅管理员可访问
"""
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import User, LedgerRecord
from app.auth.dependencies import get_current_admin
from app.schemas.auth import UserListResponse


router = APIRouter(prefix="/admin/users", tags=["用户管理"])


@router.get("", response_model=UserListResponse)
async def get_users(
    is_active: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取用户列表"""
    query = db.query(User)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    # 排除当前管理员
    query = query.filter(User.id != current_user.id)
    
    total = query.count()
    
    users = query.order_by(User.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    result = []
    for user in users:
        # 获取用户记账记录数
        record_count = db.query(func.count(LedgerRecord.id)).filter(
            LedgerRecord.user_id == user.id
        ).scalar()
        
        result.append({
            'id': user.id,
            'username': user.username,
            'is_admin': user.is_admin,
            'is_active': user.is_active,
            'record_count': record_count,
            'created_at': user.created_at.isoformat() if user.created_at else None,
        })
    
    return {"total": total, "users": result}


@router.post("/{user_id}/disable")
async def disable_user(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """禁用用户"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    if user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能禁用管理员"
        )
    
    user.is_active = False
    db.commit()
    
    return {"message": "用户已禁用"}


@router.post("/{user_id}/enable")
async def enable_user(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """启用用户"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    user.is_active = True
    db.commit()
    
    return {"message": "用户已启用"}


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """删除用户"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    if user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除管理员"
        )
    
    # 删除用户的记账记录
    db.query(LedgerRecord).filter(LedgerRecord.user_id == user_id).delete()
    
    # 删除用户
    db.delete(user)
    db.commit()
    
    return {"message": "用户已删除"}
