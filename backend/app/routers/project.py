"""
项目路由
"""
from typing import Optional, List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import User, Project, LedgerRecord
from app.auth.dependencies import get_current_user
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectStats,
    ProjectListResponse,
)


router = APIRouter(prefix="/projects", tags=["项目"])


def calculate_project_stats(db: Session, project: Project) -> ProjectStats:
    """计算项目统计"""
    total_spent = db.query(func.sum(LedgerRecord.amount)).filter(
        LedgerRecord.project_id == project.id
    ).scalar() or 0
    
    budget_usage_rate = 0
    if project.budget and project.budget > 0:
        budget_usage_rate = round((total_spent / project.budget) * 100, 2)
    
    per_person_cost = 0
    if project.member_count and project.member_count > 0:
        per_person_cost = round(total_spent / project.member_count, 2)
    
    return ProjectStats(
        total_spent=float(total_spent),
        budget_usage_rate=budget_usage_rate,
        per_person_cost=per_person_cost
    )


@router.get("")
async def get_projects(
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取项目列表"""
    query = db.query(Project).filter(Project.user_id == current_user.id)
    
    if status:
        query = query.filter(Project.status == status)
    
    total = query.count()
    
    projects = query.order_by(Project.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    result = []
    for project in projects:
        stats = calculate_project_stats(db, project)
        
        # 转换datetime为字符串
        p_dict = {
            'id': project.id,
            'user_id': project.user_id,
            'name': project.name,
            'description': project.description,
            'budget': project.budget,
            'member_count': project.member_count,
            'start_date': str(project.start_date) if project.start_date else None,
            'end_date': str(project.end_date) if project.end_date else None,
            'status': project.status,
            'stats': stats.model_dump(),
            'created_at': project.created_at.isoformat() if project.created_at else None,
            'updated_at': project.updated_at.isoformat() if project.updated_at else None,
        }
        result.append(p_dict)
    
    return {"total": total, "projects": result}


@router.get("/{project_id}")
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取项目详情"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    stats = calculate_project_stats(db, project)
    
    return {
        'id': project.id,
        'user_id': project.user_id,
        'name': project.name,
        'description': project.description,
        'budget': project.budget,
        'member_count': project.member_count,
        'start_date': str(project.start_date) if project.start_date else None,
        'end_date': str(project.end_date) if project.end_date else None,
        'status': project.status,
        'stats': stats.model_dump(),
        'created_at': project.created_at.isoformat() if project.created_at else None,
        'updated_at': project.updated_at.isoformat() if project.updated_at else None,
    }


@router.post("")
async def create_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建项目"""
    # 验证时间范围
    if project.start_date and project.end_date:
        if project.start_date > project.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="开始日期不能晚于结束日期"
            )
    
    db_project = Project(
        user_id=current_user.id,
        **project.model_dump()
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    stats = ProjectStats()
    
    return {
        'id': db_project.id,
        'user_id': db_project.user_id,
        'name': db_project.name,
        'description': db_project.description,
        'budget': db_project.budget,
        'member_count': db_project.member_count,
        'start_date': str(db_project.start_date) if db_project.start_date else None,
        'end_date': str(db_project.end_date) if db_project.end_date else None,
        'status': db_project.status,
        'stats': stats.model_dump(),
        'created_at': db_project.created_at.isoformat() if db_project.created_at else None,
        'updated_at': db_project.updated_at.isoformat() if db_project.updated_at else None,
    }


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新项目"""
    db_project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 验证时间范围
    start_date = project_update.start_date or db_project.start_date
    end_date = project_update.end_date or db_project.end_date
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="开始日期不能晚于结束日期"
        )
    
    for key, value in project_update.model_dump(exclude_unset=True).items():
        setattr(db_project, key, value)
    
    db.commit()
    db.refresh(db_project)
    
    stats = calculate_project_stats(db, db_project)
    
    return {
        'id': db_project.id,
        'user_id': db_project.user_id,
        'name': db_project.name,
        'description': db_project.description,
        'budget': db_project.budget,
        'member_count': db_project.member_count,
        'start_date': str(db_project.start_date) if db_project.start_date else None,
        'end_date': str(db_project.end_date) if db_project.end_date else None,
        'status': db_project.status,
        'stats': stats.model_dump(),
        'created_at': db_project.created_at.isoformat() if db_project.created_at else None,
        'updated_at': db_project.updated_at.isoformat() if db_project.updated_at else None,
    }


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除项目"""
    db_project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 删除项目的记账记录关联
    db.query(LedgerRecord).filter(
        LedgerRecord.project_id == project_id
    ).update({"project_id": None})
    
    db.delete(db_project)
    db.commit()
    
    return {"message": "删除成功"}
