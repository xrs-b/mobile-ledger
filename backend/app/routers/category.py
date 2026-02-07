"""
分类路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models import User, Category
from app.auth.dependencies import get_current_user
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryTreeResponse,
)


router = APIRouter(prefix="/categories", tags=["分类"])


@router.get("", response_model=List[CategoryResponse])
async def get_categories(
    type: Optional[str] = None,
    include_private: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取分类列表"""
    # 获取系统分类（user_id is NULL）
    query = db.query(Category)
    
    if include_private:
        # 获取当前用户的私有分类
        system_categories = query.filter(Category.user_id.is_(None))
        private_categories = query.filter(Category.user_id == current_user.id)
        categories = system_categories.union(private_categories)
    else:
        categories = query.filter(Category.user_id.is_(None))
    
    if type:
        categories = categories.filter(Category.type == type)
    
    categories = categories.order_by(Category.sort_order, Category.id).all()
    return categories


@router.get("/tree", response_model=List[CategoryTreeResponse])
async def get_category_tree(
    type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取分类树形结构"""
    # 获取一级分类
    base_query = db.query(Category).filter(Category.parent_id.is_(None))
    
    if type:
        base_query = base_query.filter(Category.type == type)
    
    # 添加用户私有的一级分类
    system_cats = base_query.filter(Category.user_id.is_(None))
    private_cats = base_query.filter(Category.user_id == current_user.id)
    parents = system_cats.union(private_cats).order_by(Category.sort_order).all()
    
    result = []
    for parent in parents:
        children = db.query(Category).filter(
            Category.parent_id == parent.id,
            or_(Category.user_id.is_(None), Category.user_id == current_user.id)
        ).order_by(Category.sort_order).all()
        
        # 转换children中的datetime为字符串
        children_data = []
        for child in children:
            children_data.append({
                'id': child.id,
                'user_id': child.user_id,
                'name': child.name,
                'parent_id': child.parent_id,
                'icon': child.icon,
                'type': child.type,
                'is_system': child.is_system,
                'sort_order': child.sort_order,
                'created_at': child.created_at.isoformat() if child.created_at else None,
                'updated_at': child.updated_at.isoformat() if child.updated_at else None,
            })
        
        result.append(CategoryTreeResponse(
            id=parent.id,
            name=parent.name,
            icon=parent.icon,
            type=parent.type,
            is_system=parent.is_system,
            children=children_data
        ))
    
    return result


@router.post("", response_model=CategoryResponse)
async def create_category(
    category: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建分类"""
    # 如果是一级分类，不需要parent_id
    if category.parent_id:
        # 验证父分类存在且属于系统或当前用户
        parent = db.query(Category).filter(Category.id == category.parent_id).first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="父分类不存在"
            )
        if parent.user_id and parent.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="不能使用其他用户的分类"
            )
    
    db_category = Category(
        **category.dict(),
        user_id=current_user.id if category.parent_id else None,  # 一级分类属于系统
        is_system=False
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新分类"""
    db_category = db.query(Category).filter(
        Category.id == category_id,
        or_(Category.user_id.is_(None), Category.user_id == current_user.id)
    ).first()
    
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )
    
    # 系统分类只能更新icon和sort_order
    if db_category.is_system:
        update_data = category_update.model_dump(exclude_unset=True)
        if "name" in update_data:
            update_data.pop("name")
        for key, value in update_data.items():
            setattr(db_category, key, value)
    else:
        for key, value in category_update.model_dump(exclude_unset=True).items():
            setattr(db_category, key, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除分类（仅限私有分类）"""
    db_category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id  # 只能删除自己的分类
    ).first()
    
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在或无权删除"
        )
    
    # 删除子分类
    db.query(Category).filter(Category.parent_id == category_id).delete()
    
    # 删除当前分类
    db.delete(db_category)
    db.commit()
    
    return {"message": "删除成功"}
