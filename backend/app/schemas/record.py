"""
记账记录Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class RecordCreate(BaseModel):
    """创建记账请求"""
    amount: float = Field(..., gt=0)
    type: str = Field(..., pattern="^(income|expense)$")
    category_id: int
    remark: Optional[str] = Field(None, max_length=500)
    project_id: Optional[int] = None
    record_date: date = Field(default_factory=date.today)


class RecordUpdate(BaseModel):
    """更新记账请求"""
    amount: Optional[float] = Field(None, gt=0)
    category_id: Optional[int] = None
    remark: Optional[str] = Field(None, max_length=500)
    project_id: Optional[int] = None
    record_date: Optional[date] = None


class RecordResponse(BaseModel):
    """记账响应"""
    id: int
    user_id: int
    category_id: int
    amount: float
    type: str
    remark: Optional[str]
    project_id: Optional[int]
    record_date: date
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class RecordListResponse(BaseModel):
    """记账列表响应"""
    total: int
    page: int
    page_size: int
    records: List[RecordResponse]

    class Config:
        from_attributes = True


class RecordWithCategory(BaseModel):
    """带分类信息的记账记录"""
    id: int
    user_id: int
    amount: float
    type: str
    remark: Optional[str]
    project_id: Optional[int]
    record_date: date
    created_at: str
    updated_at: str
    category: dict = None
    
    class Config:
        from_attributes = True
