"""
项目Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class ProjectCreate(BaseModel):
    """创建项目请求"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    budget: float = Field(0, ge=0)
    member_count: int = Field(1, ge=1)
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class ProjectUpdate(BaseModel):
    """更新项目请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    budget: Optional[float] = Field(None, ge=0)
    member_count: Optional[int] = Field(None, ge=1)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = Field(None, pattern="^(active|completed|cancelled)$")


class ProjectStats(BaseModel):
    """项目统计"""
    total_spent: float = 0
    budget_usage_rate: float = 0
    per_person_cost: float = 0


class ProjectResponse(BaseModel):
    """项目响应"""
    id: int
    user_id: int
    name: str
    description: Optional[str]
    budget: float
    member_count: int
    start_date: Optional[date]
    end_date: Optional[date]
    status: str
    stats: Optional[ProjectStats]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """项目列表响应"""
    total: int
    projects: List[ProjectResponse]

    class Config:
        from_attributes = True
