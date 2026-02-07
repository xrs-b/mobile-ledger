"""
统计报表路由
"""
from typing import Optional, List, Dict
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import User, Category, LedgerRecord, Project
from app.auth.dependencies import get_current_user
from app.schemas.statistics import (
    DateRangeStats,
    DailyStats,
    DailyStatsResponse,
    MonthlyStats,
    MonthlyStatsResponse,
    CategoryStats,
    CategoryStatsResponse,
    TrendResponse,
    TrendDataPoint,
    OverviewResponse,
    DashboardResponse,
    TopCategory,
)


router = APIRouter(prefix="/statistics", tags=["统计报表"])


def get_date_range(year: int, month: Optional[int] = None) -> tuple:
    """获取年份或年月的起止日期"""
    if month:
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
    else:
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
    return start_date, end_date


@router.get("/overview")
async def get_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取今日和本月概览"""
    today = date.today()
    first_day = date(today.year, today.month, 1)
    
    # 今日统计
    today_records = db.query(LedgerRecord).filter(
        LedgerRecord.user_id == current_user.id,
        LedgerRecord.record_date == today
    ).all()
    today_income = sum(r.amount for r in today_records if r.type == "income")
    today_expense = sum(r.amount for r in today_records if r.type == "expense")
    
    # 本月统计
    month_records = db.query(LedgerRecord).filter(
        LedgerRecord.user_id == current_user.id,
        LedgerRecord.record_date >= first_day,
        LedgerRecord.record_date <= today
    ).all()
    month_income = sum(r.amount for r in month_records if r.type == "income")
    month_expense = sum(r.amount for r in month_records if r.type == "expense")
    
    # 活跃项目数
    active_projects = db.query(Project).filter(
        Project.user_id == current_user.id,
        Project.status == "active"
    ).count()
    
    # 最近记录数（最近7天）
    week_ago = today - timedelta(days=7)
    recent_count = db.query(LedgerRecord).filter(
        LedgerRecord.user_id == current_user.id,
        LedgerRecord.record_date >= week_ago
    ).count()
    
    return OverviewResponse(
        today_income=today_income,
        today_expense=today_expense,
        today_balance=today_income - today_expense,
        month_income=month_income,
        month_expense=month_expense,
        month_balance=month_income - month_expense,
        active_projects=active_projects,
        recent_records_count=recent_count
    )


@router.get("/daily", response_model=DailyStatsResponse)
async def get_daily_stats(
    year: int = Query(..., ge=2020, le=2100),
    month: Optional[int] = Query(None, ge=1, le=12),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取每日统计"""
    if month:
        start_date, end_date = get_date_range(year, month)
    else:
        start_date, end_date = get_date_range(year)
    
    # 获取该范围内所有记录
    records = db.query(LedgerRecord).filter(
        LedgerRecord.user_id == current_user.id,
        LedgerRecord.record_date >= start_date,
        LedgerRecord.record_date <= end_date
    ).all()
    
    # 按日期分组
    daily_data = {}
    for r in records:
        date_str = str(r.record_date)
        if date_str not in daily_data:
            daily_data[date_str] = {"income": 0, "expense": 0}
        if r.type == "income":
            daily_data[date_str]["income"] += r.amount
        else:
            daily_data[date_str]["expense"] += r.amount
    
    # 填充所有日期
    stats = []
    current = start_date
    while current <= end_date:
        date_str = str(current)
        income = daily_data.get(date_str, {}).get("income", 0)
        expense = daily_data.get(date_str, {}).get("expense", 0)
        stats.append(DailyStats(
            date=date_str,
            income=income,
            expense=expense,
            balance=income - expense
        ))
        current += timedelta(days=1)
    
    total_income = sum(s.income for s in stats)
    total_expense = sum(s.expense for s in stats)
    
    return DailyStatsResponse(
        stats=stats,
        total_income=total_income,
        total_expense=total_expense,
        total_days=len(stats)
    )


@router.get("/monthly", response_model=MonthlyStatsResponse)
async def get_monthly_stats(
    year: int = Query(..., ge=2020, le=2100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取月度统计"""
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    
    # 获取该年度所有记录
    records = db.query(LedgerRecord).filter(
        LedgerRecord.user_id == current_user.id,
        LedgerRecord.record_date >= start_date,
        LedgerRecord.record_date <= end_date
    ).all()
    
    # 按年月分组
    monthly_data = {}
    for r in records:
        key = (r.record_date.year, r.record_date.month)
        if key not in monthly_data:
            monthly_data[key] = {"income": 0, "expense": 0, "count": 0}
        monthly_data[key]["count"] += 1
        if r.type == "income":
            monthly_data[key]["income"] += r.amount
        else:
            monthly_data[key]["expense"] += r.amount
    
    # 填充所有月份
    stats = []
    for month in range(1, 13):
        key = (year, month)
        income = monthly_data.get(key, {}).get("income", 0)
        expense = monthly_data.get(key, {}).get("expense", 0)
        count = monthly_data.get(key, {}).get("count", 0)
        stats.append(MonthlyStats(
            year=year,
            month=month,
            income=income,
            expense=expense,
            balance=income - expense,
            record_count=count
        ))
    
    total_income = sum(s.income for s in stats)
    total_expense = sum(s.expense for s in stats)
    
    return MonthlyStatsResponse(
        stats=stats,
        total_income=total_income,
        total_expense=total_expense,
        total_months=12
    )


@router.get("/category", response_model=CategoryStatsResponse)
async def get_category_stats(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    record_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取分类统计"""
    query = db.query(
        LedgerRecord.category_id,
        func.sum(LedgerRecord.amount).label("total"),
        func.count(LedgerRecord.id).label("count")
    ).filter(LedgerRecord.user_id == current_user.id)
    
    if start_date:
        query = query.filter(LedgerRecord.record_date >= start_date)
    if end_date:
        query = query.filter(LedgerRecord.record_date <= end_date)
    if record_type:
        query = query.filter(LedgerRecord.type == record_type)
    
    results = query.group_by(LedgerRecord.category_id).all()
    
    # 获取分类信息
    categories = {c.id: c for c in db.query(Category).all()}
    
    # 计算总金额
    total_amount = sum(r.total for r in results) or 1
    
    # 构建统计
    category_stats = []
    for r in results:
        cat = categories.get(r.category_id)
        if cat:
            percentage = (r.total / total_amount * 100) if total_amount > 0 else 0
            category_stats.append(CategoryStats(
                category_id=r.category_id,
                category_name=cat.name,
                category_icon=cat.icon,
                parent_id=cat.parent_id,
                type=cat.type,
                total_amount=float(r.total),
                percentage=round(percentage, 2),
                count=r.count
            ))
    
    # 按金额排序
    category_stats.sort(key=lambda x: x.total_amount, reverse=True)
    
    stat_type = record_type or "both"
    
    return CategoryStatsResponse(
        type=stat_type,
        total_amount=total_amount,
        categories=category_stats
    )


@router.get("/trend", response_model=TrendResponse)
async def get_trend(
    days: int = Query(30, ge=1, le=365),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    record_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取收支趋势"""
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=days - 1)
    
    query = db.query(
        LedgerRecord.record_date,
        LedgerRecord.type,
        func.sum(LedgerRecord.amount).label("total")
    ).filter(LedgerRecord.user_id == current_user.id)
    
    if start_date:
        query = query.filter(LedgerRecord.record_date >= start_date)
    if end_date:
        query = query.filter(LedgerRecord.record_date <= end_date)
    if record_type:
        query = query.filter(LedgerRecord.type == record_type)
    
    results = query.group_by(
        LedgerRecord.record_date,
        LedgerRecord.type
    ).order_by(LedgerRecord.record_date).all()
    
    # 整理数据
    daily_data = {}
    for r in results:
        date_str = str(r.record_date)
        if date_str not in daily_data:
            daily_data[date_str] = {"income": 0, "expense": 0}
        if r.type == "income":
            daily_data[date_str]["income"] = float(r.total)
        else:
            daily_data[date_str]["expense"] = float(r.total)
    
    # 构建趋势数据
    trend = []
    current = start_date
    while current <= end_date:
        date_str = str(current)
        income = daily_data.get(date_str, {}).get("income", 0)
        expense = daily_data.get(date_str, {}).get("expense", 0)
        
        if record_type == "income":
            value = income
        elif record_type == "expense":
            value = expense
        else:
            value = income - expense
        
        trend.append(TrendDataPoint(date=date_str, value=value))
        current += timedelta(days=1)
    
    # 计算统计
    values = [t.value for t in trend]
    avg_daily = sum(values) / len(values) if values else 0
    max_value = max(values) if values else 0
    min_value = min(values) if values else 0
    
    # 计算环比增长率
    growth_rate = None
    if len(values) >= 2:
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        first_avg = sum(first_half) / len(first_half) if first_half else 0
        second_avg = sum(second_half) / len(second_half) if second_half else 0
        if first_avg > 0:
            growth_rate = round((second_avg - first_avg) / first_avg * 100, 2)
    
    return TrendResponse(
        type=record_type or "both",
        trend=trend,
        avg_daily=round(avg_daily, 2),
        max_value=round(max_value, 2),
        min_value=round(min_value, 2),
        growth_rate=growth_rate
    )


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    days: int = Query(7, ge=1, le=30),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取仪表盘数据"""
    today = date.today()
    start_date = today - timedelta(days=days - 1)
    
    # 概览
    overview = await get_overview(current_user, db)
    
    # 最近记录
    recent_records = db.query(LedgerRecord).filter(
        LedgerRecord.user_id == current_user.id,
        LedgerRecord.record_date >= start_date
    ).order_by(
        LedgerRecord.record_date.desc(),
        LedgerRecord.created_at.desc()
    ).limit(10).all()
    
    recent_data = []
    categories = {c.id: c for c in db.query(Category).all()}
    for r in recent_records:
        cat = categories.get(r.category_id)
        recent_data.append({
            'id': r.id,
            'amount': r.amount,
            'type': r.type,
            'category_name': cat.name if cat else '未知',
            'category_icon': cat.icon if cat else None,
            'remark': r.remark,
            'record_date': str(r.record_date)
        })
    
    # TOP收入分类
    income_stats = await get_category_stats(
        start_date=start_date,
        end_date=today,
        record_type="income",
        current_user=current_user,
        db=db
    )
    top_income = [
        TopCategory(
            category_id=c.category_id,
            category_name=c.category_name,
            icon=c.category_icon,
            amount=c.total_amount,
            percentage=c.percentage
        )
        for c in income_stats.categories[:5]
    ]
    
    # TOP支出分类
    expense_stats = await get_category_stats(
        start_date=start_date,
        end_date=today,
        record_type="expense",
        current_user=current_user,
        db=db
    )
    top_expense = [
        TopCategory(
            category_id=c.category_id,
            category_name=c.category_name,
            icon=c.category_icon,
            amount=c.total_amount,
            percentage=c.percentage
        )
        for c in expense_stats.categories[:5]
    ]
    
    # 每日趋势
    daily_stats = await get_daily_stats(
        year=today.year,
        month=today.month,
        current_user=current_user,
        db=db
    )
    daily_trend = [
        TrendDataPoint(date=s.date, value=s.balance)
        for s in daily_stats.stats[-days:]
    ]
    
    # 月度趋势（最近6个月）
    monthly_trend = await get_monthly_trends(db, current_user)
    
    return DashboardResponse(
        overview=overview,
        recent_records=recent_data,
        top_income_categories=top_income,
        top_expense_categories=top_expense,
        daily_trend=daily_trend,
        monthly_trend=monthly_trend
    )


async def get_monthly_trends(db: Session, current_user: User) -> List[MonthlyStats]:
    """获取最近6个月的趋势"""
    today = date.today()
    trends = []
    
    for i in range(5, -1, -1):
        month = today.month - i
        year = today.year
        
        if month <= 0:
            month += 12
            year -= 1
        
        _, end_date = get_date_range(year, month)
        start_date = date(year, month, 1)
        
        records = db.query(LedgerRecord).filter(
            LedgerRecord.user_id == current_user.id,
            LedgerRecord.record_date >= start_date,
            LedgerRecord.record_date <= end_date
        ).all()
        
        income = sum(r.amount for r in records if r.type == "income")
        expense = sum(r.amount for r in records if r.type == "expense")
        
        trends.append(MonthlyStats(
            year=year,
            month=month,
            income=income,
            expense=expense,
            balance=income - expense,
            record_count=len(records)
        ))
    
    return trends


@router.get("/yearly")
async def get_yearly_stats(
    year: int = Query(..., ge=2020, le=2100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取年度统计"""
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    
    # 年度总览
    records = db.query(LedgerRecord).filter(
        LedgerRecord.user_id == current_user.id,
        LedgerRecord.record_date >= start_date,
        LedgerRecord.record_date <= end_date
    ).all()
    
    total_income = sum(r.amount for r in records if r.type == "income")
    total_expense = sum(r.amount for r in records if r.type == "expense")
    
    # 月度分布
    monthly_stats = await get_monthly_stats(year, current_user, db)
    
    # 分类分布
    category_stats = await get_category_stats(
        start_date=start_date,
        end_date=end_date,
        current_user=current_user,
        db=db
    )
    
    # 年度对比（与上一年）
    prev_year = year - 1
    prev_start = date(prev_year, 1, 1)
    prev_end = date(prev_year, 12, 31)
    
    prev_records = db.query(LedgerRecord).filter(
        LedgerRecord.user_id == current_user.id,
        LedgerRecord.record_date >= prev_start,
        LedgerRecord.record_date <= prev_end
    ).all()
    
    prev_income = sum(r.amount for r in prev_records if r.type == "income")
    prev_expense = sum(r.amount for r in prev_records if r.type == "expense")
    
    income_change = ((total_income - prev_income) / prev_income * 100) if prev_income > 0 else None
    expense_change = ((total_expense - prev_expense) / prev_expense * 100) if prev_expense > 0 else None
    
    return {
        "year": year,
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": total_income - total_expense,
        "record_count": len(records),
        "monthly_stats": monthly_stats.model_dump(),
        "category_stats": category_stats.model_dump(),
        "year_over_year": {
            "prev_year": prev_year,
            "prev_income": prev_income,
            "prev_expense": prev_expense,
            "income_change": round(income_change, 2) if income_change is not None else None,
            "expense_change": round(expense_change, 2) if expense_change is not None else None
        }
    }


@router.get("/compare/months")
async def compare_months(
    month1: int = Query(..., ge=1, le=12),
    year1: int = Query(..., ge=2020, le=2100),
    month2: int = Query(..., ge=1, le=12),
    year2: int = Query(..., ge=2020, le=2100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """对比两个月的收支"""
    def get_month_data(year: int, month: int):
        start_date, end_date = get_date_range(year, month)
        records = db.query(LedgerRecord).filter(
            LedgerRecord.user_id == current_user.id,
            LedgerRecord.record_date >= start_date,
            LedgerRecord.record_date <= end_date
        ).all()
        
        income = sum(r.amount for r in records if r.type == "income")
        expense = sum(r.amount for r in records if r.type == "expense")
        
        # 按分类统计
        cat_data = {}
        for r in records:
            if r.type not in cat_data:
                cat_data[r.type] = {}
            if r.category_id not in cat_data[r.type]:
                cat_data[r.type][r.category_id] = 0
            cat_data[r.type][r.category_id] += r.amount
        
        return {
            "year": year,
            "month": month,
            "income": income,
            "expense": expense,
            "balance": income - expense,
            "record_count": len(records),
            "category_breakdown": cat_data
        }
    
    data1 = get_month_data(year1, month1)
    data2 = get_month_data(year2, month2)
    
    income_change = ((data2["income"] - data1["income"]) / data1["income"] * 100) if data1["income"] > 0 else None
    expense_change = ((data2["expense"] - data1["expense"]) / data1["expense"] * 100) if data1["expense"] > 0 else None
    
    return {
        "period1": data1,
        "period2": data2,
        "comparison": {
            "income_change": round(income_change, 2) if income_change is not None else None,
            "expense_change": round(expense_change, 2) if expense_change is not None else None
        }
    }


@router.get("/compare/categories")
async def compare_categories(
    start_date1: Optional[date] = None,
    end_date1: Optional[date] = None,
    start_date2: Optional[date] = None,
    end_date2: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """对比两个时间段的分类支出"""
    today = date.today()
    if not end_date1:
        end_date1 = today
    if not start_date1:
        start_date1 = today - timedelta(days=30)
    if not end_date2:
        end_date2 = today - timedelta(days=30)
    if not start_date2:
        start_date2 = end_date2 - timedelta(days=30)
    
    def get_category_data(start: date, end: date):
        records = db.query(LedgerRecord).filter(
            LedgerRecord.user_id == current_user.id,
            LedgerRecord.record_date >= start,
            LedgerRecord.record_date <= end,
            LedgerRecord.type == "expense"
        ).all()
        
        cat_totals = {}
        for r in records:
            if r.category_id not in cat_totals:
                cat_totals[r.category_id] = 0
            cat_totals[r.category_id] += r.amount
        
        categories = {c.id: c for c in db.query(Category).all()}
        
        result = []
        for cat_id, total in cat_totals.items():
            cat = categories.get(cat_id)
            if cat:
                result.append({
                    "category_id": cat_id,
                    "category_name": cat.name,
                    "icon": cat.icon,
                    "total": total
                })
        
        result.sort(key=lambda x: x["total"], reverse=True)
        return result
    
    data1 = get_category_data(start_date1, end_date1)
    data2 = get_category_data(start_date2, end_date2)
    
    cat_ids1 = set(d["category_id"] for d in data1)
    cat_ids2 = set(d["category_id"] for d in data2)
    
    new_categories = cat_ids2 - cat_ids1
    vanished_categories = cat_ids1 - cat_ids2
    
    return {
        "period1": {"start": str(start_date1), "end": str(end_date1), "categories": data1},
        "period2": {"start": str(start_date2), "end": str(end_date2), "categories": data2},
        "new_categories": list(new_categories),
        "vanished_categories": list(vanished_categories)
    }
