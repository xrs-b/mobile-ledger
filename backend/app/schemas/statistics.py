"""
统计报表Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class DateRangeStats(BaseModel):
    """日期范围统计"""
    start_date: str
    end_date: str
    total_income: float = 0
    total_expense: float = 0
    balance: float = 0
    record_count: int = 0


class DailyStats(BaseModel):
    """单日统计"""
    date: str
    income: float = 0
    expense: float = 0
    balance: float = 0


class DailyStatsResponse(BaseModel):
    """每日统计列表"""
    stats: List[DailyStats]
    total_income: float
    total_expense: float
    total_days: int


class MonthlyStats(BaseModel):
    """单月统计"""
    year: int
    month: int
    income: float = 0
    expense: float = 0
    balance: float = 0
    record_count: int = 0


class MonthlyStatsResponse(BaseModel):
    """月度统计列表"""
    stats: List[MonthlyStats]
    total_income: float
    total_expense: float
    total_months: int


class CategoryStats(BaseModel):
    """分类统计"""
    category_id: int
    category_name: str
    category_icon: Optional[str] = None
    parent_id: Optional[int] = None
    type: str  # income/expense
    total_amount: float = 0
    percentage: float = 0
    count: int = 0


class CategoryStatsResponse(BaseModel):
    """分类统计列表"""
    type: str  # income/expense
    total_amount: float
    categories: List[CategoryStats]


class ProjectStatsResponse(BaseModel):
    """项目统计响应"""
    id: int
    name: str
    budget: float
    total_spent: float
    budget_usage_rate: float  # 百分比
    per_person_cost: float
    member_count: int
    status: str


class TrendDataPoint(BaseModel):
    """趋势数据点"""
    date: str
    value: float


class TrendResponse(BaseModel):
    """趋势分析响应"""
    type: str  # income/expense/both
    trend: List[TrendDataPoint]
    avg_daily: float
    max_value: float
    min_value: float
    growth_rate: Optional[float] = None  # 环比增长率


class OverviewResponse(BaseModel):
    """概览数据"""
    today_income: float
    today_expense: float
    today_balance: float
    month_income: float
    month_expense: float
    month_balance: float
    month_budget_usage: Optional[float] = None
    active_projects: int
    recent_records_count: int


class TopCategory(BaseModel):
    """TOP分类"""
    category_id: int
    category_name: str
    icon: Optional[str] = None
    amount: float
    percentage: float


class DashboardResponse(BaseModel):
    """仪表盘数据"""
    overview: OverviewResponse
    recent_records: List[dict] = []
    top_income_categories: List[TopCategory] = []
    top_expense_categories: List[TopCategory] = []
    daily_trend: List[TrendDataPoint] = []
    monthly_trend: List[MonthlyStats] = []
