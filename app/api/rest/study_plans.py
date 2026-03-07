"""
Study Plans REST endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.planning import StudyPlan
from app.schemas.planning import StudyPlanCreate, StudyPlanUpdate, StudyPlanResponse

router = APIRouter(prefix="/study-plans", tags=["study-plans"])


@router.get("", response_model=List[StudyPlanResponse])
async def get_study_plans(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's study plans."""
    query = select(StudyPlan).where(StudyPlan.user_id == current_user.id)
    query = query.order_by(StudyPlan.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    study_plans = result.scalars().all()
    return study_plans


@router.get("/{study_plan_id}", response_model=StudyPlanResponse)
async def get_study_plan(
    study_plan_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific study plan."""
    result = await db.execute(
        select(StudyPlan).where(and_(StudyPlan.id == study_plan_id, StudyPlan.user_id == current_user.id))
    )
    study_plan = result.scalar_one_or_none()
    
    if not study_plan:
        raise HTTPException(status_code=404, detail="Study plan not found")
    
    return study_plan


@router.post("", response_model=StudyPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_study_plan(
    study_plan_data: StudyPlanCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new study plan."""
    plan_dict = study_plan_data.model_dump()
    # Convert empty strings to None for optional fields
    if plan_dict.get("description") == "":
        plan_dict["description"] = None
    if plan_dict.get("plan_content") == "":
        plan_dict["plan_content"] = None
    
    new_study_plan = StudyPlan(
        **plan_dict,
        user_id=current_user.id
    )
    
    db.add(new_study_plan)
    await db.commit()
    await db.refresh(new_study_plan)
    
    return new_study_plan


@router.put("/{study_plan_id}", response_model=StudyPlanResponse)
async def update_study_plan(
    study_plan_id: int,
    study_plan_data: StudyPlanUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a study plan."""
    result = await db.execute(
        select(StudyPlan).where(and_(StudyPlan.id == study_plan_id, StudyPlan.user_id == current_user.id))
    )
    study_plan = result.scalar_one_or_none()
    
    if not study_plan:
        raise HTTPException(status_code=404, detail="Study plan not found")
    
    # Update fields - only update provided fields
    update_data = study_plan_data.model_dump(exclude_unset=True)
    # Convert empty strings to None for optional fields
    for field, value in update_data.items():
        if value == "":
            value = None
        setattr(study_plan, field, value)
    
    await db.commit()
    await db.refresh(study_plan)
    
    return study_plan


@router.delete("/{study_plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_study_plan(
    study_plan_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a study plan."""
    result = await db.execute(
        select(StudyPlan).where(and_(StudyPlan.id == study_plan_id, StudyPlan.user_id == current_user.id))
    )
    study_plan = result.scalar_one_or_none()
    
    if not study_plan:
        raise HTTPException(status_code=404, detail="Study plan not found")
    
    await db.delete(study_plan)
    await db.commit()
    
    return None

