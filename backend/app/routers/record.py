"""
记账记录路由
"""
from typing import Optional, List
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.database import get_db
from app.models import User, Category, LedgerRecord, Project
from app.auth.dependencies import get_current_user
from app.schemas.record import (
    RecordCreate,
    RecordUpdate,
    RecordResponse,
    RecordListResponse,
)


router = APIRouter(prefix="/records", tags=["记账"])


@router.get("")
async def get_records(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    record_type: Optional[str] = Query(None, alias="type"),
    category_id: Optional[int] = None,
    project_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取记账列表"""
    query = db.query(LedgerRecord).filter(LedgerRecord.user_id == current_user.id)
    
    if start_date:
        query = query.filter(LedgerRecord.record_date >= start_date)
    if end_date:
        query = query.filter(LedgerRecord.record_date <= end_date)
    if record_type:
        query = query.filter(LedgerRecord.type == record_type)
    if category_id:
        query = query.filter(LedgerRecord.category_id == category_id)
    if project_id is not None:
        query = query.filter(LedgerRecord.project_id == project_id)
    
    # 统计总数
    total = query.count()
    
    # 分页查询
    records = query.order_by(
        LedgerRecord.record_date.desc(),
        LedgerRecord.created_at.desc()
    ).offset((page - 1) * page_size).limit(page_size).all()
    
    # 转换records为字典列表
    records_data = []
    for r in records:
        records_data.append({
            'id': r.id,
            'user_id': r.user_id,
            'category_id': r.category_id,
            'amount': r.amount,
            'type': r.type,
            'remark': r.remark,
            'project_id': r.project_id,
            'record_date': str(r.record_date),
            'created_at': r.created_at.isoformat() if r.created_at else None,
            'updated_at': r.updated_at.isoformat() if r.updated_at else None,
        })
    
    return RecordListResponse(
        total=total,
        page=page,
        page_size=page_size,
        records=records_data
    )


@router.get("/summary")
async def get_records_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取记账汇总"""
    query = db.query(LedgerRecord).filter(LedgerRecord.user_id == current_user.id)
    
    # 添加日期过滤
    if start_date:
        query = query.filter(LedgerRecord.record_date >= start_date)
    if end_date:
        query = query.filter(LedgerRecord.record_date <= end_date)
    
    # 按类型汇总
    summary_by_type = db.query(
        LedgerRecord.type,
        func.sum(LedgerRecord.amount).label("total")
    ).filter(LedgerRecord.user_id == current_user.id)
    
    if start_date:
        summary_by_type = summary_by_type.filter(LedgerRecord.record_date >= start_date)
    if end_date:
        summary_by_type = summary_by_type.filter(LedgerRecord.record_date <= end_date)
    
    summary_by_type = summary_by_type.group_by(LedgerRecord.type).all()
    
    income = sum(r.total for r in summary_by_type if r.type == "income")
    expense = sum(r.total for r in summary_by_type if r.type == "expense")
    
    return {
        "total_income": income or 0,
        "total_expense": expense or 0,
        "balance": (income or 0) - (expense or 0),
        "start_date": str(start_date) if start_date else None,
        "end_date": str(end_date) if end_date else None
    }


@router.post("", response_model=RecordResponse)
async def create_record(
    record: RecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建记账"""
    # 验证分类存在
    category = db.query(Category).filter(
        Category.id == record.category_id,
        or_(Category.user_id.is_(None), Category.user_id == current_user.id)
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )
    
    # 验证项目（如果指定）
    if record.project_id:
        project = db.query(Project).filter(
            Project.id == record.project_id,
            Project.user_id == current_user.id
        ).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
    
    db_record = LedgerRecord(
        user_id=current_user.id,
        **record.model_dump()
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    
    # 转换datetime为字符串
    return {
        'id': db_record.id,
        'user_id': db_record.user_id,
        'category_id': db_record.category_id,
        'amount': db_record.amount,
        'type': db_record.type,
        'remark': db_record.remark,
        'project_id': db_record.project_id,
        'record_date': str(db_record.record_date),
        'created_at': db_record.created_at.isoformat() if db_record.created_at else None,
        'updated_at': db_record.updated_at.isoformat() if db_record.updated_at else None,
    }


@router.put("/{record_id}", response_model=dict)
async def update_record(
    record_id: int,
    record_update: RecordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新记账"""
    db_record = db.query(LedgerRecord).filter(
        LedgerRecord.id == record_id,
        LedgerRecord.user_id == current_user.id
    ).first()
    
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记录不存在"
        )
    
    # 验证分类（如果更新）
    if record_update.category_id:
        category = db.query(Category).filter(
            Category.id == record_update.category_id,
            or_(Category.user_id.is_(None), Category.user_id == current_user.id)
        ).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="分类不存在"
            )
    
    for key, value in record_update.model_dump(exclude_unset=True).items():
        setattr(db_record, key, value)
    
    db.commit()
    db.refresh(db_record)
    
    # 转换datetime为字符串
    return {
        'id': db_record.id,
        'user_id': db_record.user_id,
        'category_id': db_record.category_id,
        'amount': db_record.amount,
        'type': db_record.type,
        'remark': db_record.remark,
        'project_id': db_record.project_id,
        'record_date': str(db_record.record_date),
        'created_at': db_record.created_at.isoformat() if db_record.created_at else None,
        'updated_at': db_record.updated_at.isoformat() if db_record.updated_at else None,
    }


@router.delete("/{record_id}")
async def delete_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除记账"""
    db_record = db.query(LedgerRecord).filter(
        LedgerRecord.id == record_id,
        LedgerRecord.user_id == current_user.id
    ).first()
    
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记录不存在"
        )
    
    db.delete(db_record)
    db.commit()
    return {"message": "删除成功"}
