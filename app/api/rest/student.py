"""
Student-related REST endpoints: Academic Projects, Extra Activities.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.student import AcademicProject, ExtraActivity
from app.schemas.student import (
    AcademicProjectCreate, AcademicProjectUpdate, AcademicProjectResponse,
    ExtraActivityCreate, ExtraActivityUpdate, ExtraActivityResponse
)

router = APIRouter(tags=["student"])


# Academic Projects endpoints
@router.get("/academic-projects", response_model=List[AcademicProjectResponse])
async def get_academic_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's academic projects."""
    query = select(AcademicProject).where(AcademicProject.user_id == current_user.id)
    query = query.order_by(AcademicProject.start_date.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    projects = result.scalars().all()
    return projects


@router.get("/academic-projects/{project_id}", response_model=AcademicProjectResponse)
async def get_academic_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific academic project."""
    result = await db.execute(
        select(AcademicProject).where(
            and_(AcademicProject.id == project_id, AcademicProject.user_id == current_user.id)
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Academic project not found")
    
    return project


@router.post("/academic-projects", response_model=AcademicProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_academic_project(
    project_data: AcademicProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new academic project."""
    new_project = AcademicProject(
        **project_data.model_dump(),
        user_id=current_user.id
    )
    
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    
    return new_project


@router.put("/academic-projects/{project_id}", response_model=AcademicProjectResponse)
async def update_academic_project(
    project_id: int,
    project_data: AcademicProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update an academic project."""
    result = await db.execute(
        select(AcademicProject).where(
            and_(AcademicProject.id == project_id, AcademicProject.user_id == current_user.id)
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Academic project not found")
    
    # Update fields
    update_data = project_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    await db.commit()
    await db.refresh(project)
    
    return project


@router.delete("/academic-projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_academic_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an academic project."""
    result = await db.execute(
        select(AcademicProject).where(
            and_(AcademicProject.id == project_id, AcademicProject.user_id == current_user.id)
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Academic project not found")
    
    await db.delete(project)
    await db.commit()
    
    return None


# Extra Activities endpoints
@router.get("/extra-activities", response_model=List[ExtraActivityResponse])
async def get_extra_activities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's extra activities."""
    query = select(ExtraActivity).where(ExtraActivity.user_id == current_user.id)
    query = query.order_by(ExtraActivity.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    activities = result.scalars().all()
    return activities


@router.get("/extra-activities/{activity_id}", response_model=ExtraActivityResponse)
async def get_extra_activity(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific extra activity."""
    result = await db.execute(
        select(ExtraActivity).where(
            and_(ExtraActivity.id == activity_id, ExtraActivity.user_id == current_user.id)
        )
    )
    activity = result.scalar_one_or_none()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Extra activity not found")
    
    return activity


@router.post("/extra-activities", response_model=ExtraActivityResponse, status_code=status.HTTP_201_CREATED)
async def create_extra_activity(
    activity_data: ExtraActivityCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new extra activity."""
    new_activity = ExtraActivity(
        **activity_data.model_dump(),
        user_id=current_user.id
    )
    
    db.add(new_activity)
    await db.commit()
    await db.refresh(new_activity)
    
    return new_activity


@router.put("/extra-activities/{activity_id}", response_model=ExtraActivityResponse)
async def update_extra_activity(
    activity_id: int,
    activity_data: ExtraActivityUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update an extra activity."""
    result = await db.execute(
        select(ExtraActivity).where(
            and_(ExtraActivity.id == activity_id, ExtraActivity.user_id == current_user.id)
        )
    )
    activity = result.scalar_one_or_none()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Extra activity not found")
    
    # Update fields
    update_data = activity_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(activity, field, value)
    
    await db.commit()
    await db.refresh(activity)
    
    return activity


@router.delete("/extra-activities/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_extra_activity(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an extra activity."""
    result = await db.execute(
        select(ExtraActivity).where(
            and_(ExtraActivity.id == activity_id, ExtraActivity.user_id == current_user.id)
        )
    )
    activity = result.scalar_one_or_none()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Extra activity not found")
    
    await db.delete(activity)
    await db.commit()
    
    return None

