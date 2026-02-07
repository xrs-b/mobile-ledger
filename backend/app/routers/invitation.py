"""
邀请码管理路由
"""
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import User, InvitationCode
from app.auth.dependencies import get_current_admin
from app.schemas.invitation_code import (
    InvitationCodeCreate,
    InvitationCodeResponse,
    InvitationCodeListResponse,
)


router = APIRouter(prefix="/invitations", tags=["邀请码管理"])


@router.get("", response_model=InvitationCodeListResponse)
async def get_invitation_codes(
    is_used: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取邀请码列表"""
    query = db.query(InvitationCode)
    
    if is_used is not None:
        query = query.filter(InvitationCode.is_used == is_used)
    
    total = query.count()
    
    codes = query.order_by(InvitationCode.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    result = []
    for code in codes:
        # 获取创建者信息
        creator = db.query(User).filter(User.id == code.created_by).first()
        creator_name = creator.username if creator else '系统'
        
        # 获取使用者信息
        user = None
        if code.used_by:
            user = db.query(User).filter(User.id == code.used_by).first()
        used_by_name = user.username if user else None
        
        result.append({
            'id': code.id,
            'code': code.code,
            'is_used': code.is_used,
            'used_by': code.used_by,
            'used_by_name': used_by_name,
            'used_at': code.used_at.isoformat() if code.used_at else None,
            'created_by': code.created_by,
            'created_by_name': creator_name,
            'expires_at': code.expires_at.isoformat() if code.expires_at else None,
            'created_at': code.created_at.isoformat() if code.created_at else None,
        })
    
    return {"total": total, "codes": result}


@router.post("", response_model=InvitationCodeResponse)
async def create_invitation_code(
    request: InvitationCodeCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """创建邀请码"""
    # 检查邀请码是否已存在
    existing = db.query(InvitationCode).filter(
        InvitationCode.code == request.code
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邀请码已存在"
        )
    
    # 计算过期时间
    expires_at = None
    if request.valid_days:
        from datetime import timedelta
        expires_at = date.today() + timedelta(days=request.valid_days)
    
    invitation = InvitationCode(
        code=request.code,
        is_used=False,
        created_by=current_user.id,
        expires_at=expires_at
    )
    
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    
    return {
        'id': invitation.id,
        'code': invitation.code,
        'is_used': invitation.is_used,
        'expires_at': str(invitation.expires_at) if invitation.expires_at else None,
        'created_at': invitation.created_at.isoformat() if invitation.created_at else None,
    }


@router.delete("/{code_id}")
async def delete_invitation_code(
    code_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """删除邀请码"""
    code = db.query(InvitationCode).filter(InvitationCode.id == code_id).first()
    
    if not code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="邀请码不存在"
        )
    
    if code.is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已使用的邀请码不能删除"
        )
    
    db.delete(code)
    db.commit()
    
    return {"message": "删除成功"}
