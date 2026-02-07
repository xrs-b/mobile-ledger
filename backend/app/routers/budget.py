"""
预算管理路由
"""
from typing import Optional, List
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import User, Category, LedgerRecord, Project, SystemConfig
from app.auth.dependencies import get_current_user
from app.schemas.budget import (
    BudgetCreate,
    BudgetUpdate,
    BudgetResponse,
    BudgetListResponse,
    BudgetStatus,
    BudgetAlert,
    BudgetSummary,
)


# 创建预算表（如果不存在）
from app.database import Base, engine
from app.models import Budget as BudgetModel

try:
    BudgetModel.__table__.create(bind=engine, checkfirst=True)
except:
    pass


router = APIRouter(prefix="/budgets", tags=["预算管理"])


def get_period_range(period: str, budget) -> tuple:
    """获取预算周期范围"""
    today = date.today()
    
    if period == "monthly":
        start = date(today.year, today.month, 1)
        if today.month == 12:
            end = date(today.year + 1, 1, 1) - timedelta(days=1)
        else:
            end = date(today.year, today.month + 1, 1) - timedelta(days=1)
    elif period == "yearly":
        start = date(today.year, 1, 1)
        end = date(today.year, 12, 31)
    elif budget.start_date and budget.end_date:
        start = budget.start_date
        end = budget.end_date
    else:
        start = date(today.year, today.month, 1)
        end = date(today.year, today.month, 31)
    
    return start, end


def calculate_budget_status(db: Session, budget, start: date, end: date) -> Optional[BudgetStatus]:
    """计算预算状态"""
    # 计算已支出
    query = db.query(func.sum(LedgerRecord.amount)).filter(
        LedgerRecord.user_id == budget.user_id,
        LedgerRecord.record_date >= start,
        LedgerRecord.record_date <= end,
        LedgerRecord.type == "expense"
    )
    
    if budget.category_id:
        query = query.filter(LedgerRecord.category_id == budget.category_id)
    
    spent = float(query.scalar() or 0)
    remaining = float(budget.amount) - spent
    usage_rate = (spent / float(budget.amount) * 100) if float(budget.amount) > 0 else 0
    
    # 计算剩余天数
    today = date.today()
    total_days = (end - start).days + 1
    days_passed = (today - start).days
    days_remaining = max(0, (end - today).days + 1)
    
    # 预测本月剩余支出
    if days_passed > 0:
        daily_avg = spent / days_passed
        projected = daily_avg * total_days
    else:
        projected = spent
    
    # 预警等级
    alert_level = "normal"
    if usage_rate >= budget.alert_threshold:
        alert_level = "warning"
    if spent >= budget.amount:
        alert_level = "critical"
    
    # 获取分类信息
    category = None
    if budget.category_id:
        category = db.query(Category).filter(Category.id == budget.category_id).first()
    
    return BudgetStatus(
        budget_id=budget.id,
        budget_name=budget.name,
        category_id=budget.category_id,
        category_name=category.name if category else None,
        category_icon=category.icon if category else None,
        planned=budget.amount,
        spent=spent,
        remaining=remaining,
        usage_rate=round(usage_rate, 2),
        alert_level=alert_level,
        days_remaining=days_remaining,
        projected_spending=round(projected, 2) if days_passed > 0 else None
    )


@router.get("", response_model=BudgetListResponse)
async def get_budgets(
    include_inactive: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取预算列表"""
    query = db.query(BudgetModel).filter(BudgetModel.user_id == current_user.id)
    
    if not include_inactive:
        query = query.filter(BudgetModel.is_active == True)
    
    budgets = query.order_by(BudgetModel.created_at.desc()).all()
    
    total_planned = 0
    total_spent = 0
    
    result = []
    for budget in budgets:
        start, end = get_period_range(budget.period, budget)
        status = calculate_budget_status(db, budget, start, end)
        
        if status:
            total_planned += budget.amount
            total_spent += status.spent
        
        result.append(BudgetResponse(
            id=budget.id,
            user_id=budget.user_id,
            category_id=budget.category_id,
            name=budget.name,
            amount=budget.amount,
            period=budget.period,
            start_date=budget.start_date,
            end_date=budget.end_date,
            alert_threshold=budget.alert_threshold,
            is_active=budget.is_active,
            status=status,
            created_at=budget.created_at.isoformat() if budget.created_at else None,
            updated_at=budget.updated_at.isoformat() if budget.updated_at else None
        ))
    
    return BudgetListResponse(
        total=len(result),
        budgets=result,
        total_planned=total_planned,
        total_spent=total_spent,
        total_remaining=total_planned - total_spent
    )


@router.post("", response_model=BudgetResponse)
async def create_budget(
    budget: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建预算"""
    # 验证分类
    if budget.category_id:
        category = db.query(Category).filter(
            Category.id == budget.category_id,
            (Category.user_id.is_(None) | (Category.user_id == current_user.id))
        ).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="分类不存在"
            )
    
    db_budget = BudgetModel(
        user_id=current_user.id,
        **budget.model_dump()
    )
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    
    return await get_budget_detail(db_budget.id, current_user, db)


@router.get("/{budget_id}", response_model=BudgetResponse)
async def get_budget_detail(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取预算详情"""
    budget = db.query(BudgetModel).filter(
        BudgetModel.id == budget_id,
        BudgetModel.user_id == current_user.id
    ).first()
    
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预算不存在"
        )
    
    start, end = get_period_range(budget.period, budget)
    status = calculate_budget_status(db, budget, start, end)
    
    return BudgetResponse(
        id=budget.id,
        user_id=budget.user_id,
        category_id=budget.category_id,
        name=budget.name,
        amount=budget.amount,
        period=budget.period,
        start_date=budget.start_date,
        end_date=budget.end_date,
        alert_threshold=budget.alert_threshold,
        is_active=budget.is_active,
        status=status,
        created_at=budget.created_at.isoformat() if budget.created_at else None,
        updated_at=budget.updated_at.isoformat() if budget.updated_at else None
    )


@router.put("/{budget_id}", response_model=BudgetResponse)
async def update_budget(
    budget_id: int,
    budget_update: BudgetUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新预算"""
    db_budget = db.query(BudgetModel).filter(
        BudgetModel.id == budget_id,
        BudgetModel.user_id == current_user.id
    ).first()
    
    if not db_budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预算不存在"
        )
    
    for key, value in budget_update.model_dump(exclude_unset=True).items():
        setattr(db_budget, key, value)
    
    db.commit()
    db.refresh(db_budget)
    
    return await get_budget_detail(db_budget.id, current_user, db)


@router.delete("/{budget_id}")
async def delete_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除预算"""
    db_budget = db.query(BudgetModel).filter(
        BudgetModel.id == budget_id,
        BudgetModel.user_id == current_user.id
    ).first()
    
    if not db_budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预算不存在"
        )
    
    db.delete(db_budget)
    db.commit()
    
    return {"message": "删除成功"}


@router.get("/summary/current", response_model=BudgetSummary)
async def get_budget_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前预算摘要"""
    today = date.today()
    start = date(today.year, today.month, 1)
    end = date(today.year, today.month, 1)
    if today.month == 12:
        end = date(today.year + 1, 1, 1) - timedelta(days=1)
    else:
        end = date(today.year, today.month + 1, 1) - timedelta(days=1)
    
    budgets = db.query(BudgetModel).filter(
        BudgetModel.user_id == current_user.id,
        BudgetModel.is_active == True,
        BudgetModel.period == "monthly"
    ).all()
    
    total_budget = sum(b.amount for b in budgets)
    total_spent = 0
    alerts = []
    category_statuses = []
    
    for budget in budgets:
        status = calculate_budget_status(db, budget, start, end)
        if status:
            total_spent += status.spent
            category_statuses.append(status)
            
            if status.alert_level in ["warning", "critical"]:
                alerts.append(BudgetAlert(
                    budget_id=budget.id,
                    budget_name=budget.name,
                    category_name=status.category_name,
                    current_spent=status.spent,
                    budget_amount=status.planned,
                    usage_rate=status.usage_rate,
                    alert_type="threshold" if status.alert_level == "warning" else "exceeded"
                ))
    
    overall_rate = (total_spent / total_budget * 100) if total_budget > 0 else 0
    
    return BudgetSummary(
        period_start=str(start),
        period_end=str(end),
        total_budget=total_budget,
        total_spent=total_spent,
        overall_usage_rate=round(overall_rate, 2),
        alerts=alerts,
        category_budgets=category_statuses
    )


@router.get("/alerts")
async def get_budget_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取预算预警"""
    today = date.today()
    start = date(today.year, today.month, 1)
    if today.month == 12:
        end = date(today.year + 1, 1, 1) - timedelta(days=1)
    else:
        end = date(today.year, today.month + 1, 1) - timedelta(days=1)
    
    budgets = db.query(BudgetModel).filter(
        BudgetModel.user_id == current_user.id,
        BudgetModel.is_active == True
    ).all()
    
    alerts = []
    for budget in budgets:
        status = calculate_budget_status(db, budget, start, end)
        if status and status.alert_level != "normal":
            alerts.append(BudgetAlert(
                budget_id=budget.id,
                budget_name=budget.name,
                category_name=status.category_name,
                current_spent=status.spent,
                budget_amount=status.planned,
                usage_rate=status.usage_rate,
                alert_type="threshold" if status.alert_level == "warning" else "exceeded"
            ))
    
    return {"alerts": alerts, "count": len(alerts)}
