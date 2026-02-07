"""
预算管理Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class BudgetCreate(BaseModel):
    """创建预算请求"""
    category_id: Optional[int] = None  # None表示总预算
    name: str = Field(..., min_length=1, max_length=100)
    amount: float = Field(..., gt=0)
    period: str = Field("monthly", pattern="^(monthly|yearly|custom)$")
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    alert_threshold: float = Field(80, ge=0, le=100)  # 百分比


class BudgetUpdate(BaseModel):
    """更新预算请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    amount: Optional[float] = Field(None, gt=0)
    alert_threshold: Optional[float] = Field(None, ge=0, le=100)
    is_active: Optional[bool] = None


class BudgetStatus(BaseModel):
    """预算状态"""
    budget_id: int
    budget_name: str
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    category_icon: Optional[str] = None
    planned: float
    spent: float
    remaining: float
    usage_rate: float  # 百分比
    alert_level: str  # normal/warning/critical
    days_remaining: int
    projected_spending: Optional[float] = None


class BudgetResponse(BaseModel):
    """预算响应"""
    id: int
    user_id: int
    category_id: Optional[int]
    name: str
    amount: float
    period: str
    start_date: Optional[date]
    end_date: Optional[date]
    alert_threshold: float
    is_active: bool
    status: Optional[BudgetStatus] = None
    created_at: str
    updated_at: str


class BudgetListResponse(BaseModel):
    """预算列表响应"""
    total: int
    budgets: List[BudgetResponse]
    total_planned: float
    total_spent: float
    total_remaining: float


class BudgetAlert(BaseModel):
    """预算预警"""
    budget_id: int
    budget_name: str
    category_name: Optional[str] = None
    current_spent: float
    budget_amount: float
    usage_rate: float
    alert_type: str  # threshold/exceeded/depleted


class BudgetSummary(BaseModel):
    """预算摘要"""
    period_start: str
    period_end: str
    total_budget: float
    total_spent: float
    overall_usage_rate: float
    alerts: List[BudgetAlert] = []
    category_budgets: List[BudgetStatus] = []
