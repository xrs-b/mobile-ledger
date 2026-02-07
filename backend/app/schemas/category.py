"""
分类Schemas
"""
from pydantic import BaseModel, Field, model_validator
from typing import Optional, List
from datetime import datetime


class CategoryCreate(BaseModel):
    """创建分类请求"""
    name: str = Field(..., min_length=1, max_length=100)
    parent_id: Optional[int] = None
    icon: Optional[str] = None
    type: str = Field(..., pattern="^(income|expense)$")
    sort_order: int = 0


class CategoryUpdate(BaseModel):
    """更新分类请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    icon: Optional[str] = None
    sort_order: Optional[int] = None


class CategoryResponse(BaseModel):
    """分类响应"""
    id: int
    user_id: Optional[int]
    name: str
    parent_id: Optional[int]
    icon: Optional[str]
    type: str
    is_system: bool
    sort_order: int
    created_at: str
    updated_at: str

    @model_validator(mode='before')
    @classmethod
    def convert_datetime_to_str(cls, data):
        if isinstance(data, dict):
            for field in ['created_at', 'updated_at']:
                if field in data and isinstance(data[field], datetime):
                    data[field] = data[field].isoformat()
        return data

    class Config:
        from_attributes = True


class CategoryTreeResponse(BaseModel):
    """分类树形结构响应"""
    id: int
    name: str
    icon: Optional[str]
    type: str
    is_system: bool
    children: List[CategoryResponse] = []

    class Config:
        from_attributes = True
