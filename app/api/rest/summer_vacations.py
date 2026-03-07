"""
Summer Vacations REST endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.planning import SummerVacation
from app.schemas.planning import SummerVacationCreate, SummerVacationUpdate, SummerVacationResponse

router = APIRouter(prefix="/summer-vacations", tags=["summer-vacations"])


@router.get("", response_model=List[SummerVacationResponse])
async def get_summer_vacations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's summer vacations."""
    query = select(SummerVacation).where(SummerVacation.user_id == current_user.id)
    query = query.order_by(SummerVacation.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    summer_vacations = result.scalars().all()
    return summer_vacations


@router.get("/{summer_vacation_id}", response_model=SummerVacationResponse)
async def get_summer_vacation(
    summer_vacation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific summer vacation."""
    result = await db.execute(
        select(SummerVacation).where(and_(SummerVacation.id == summer_vacation_id, SummerVacation.user_id == current_user.id))
    )
    summer_vacation = result.scalar_one_or_none()
    
    if not summer_vacation:
        raise HTTPException(status_code=404, detail="Summer vacation not found")
    
    return summer_vacation


@router.post("", response_model=SummerVacationResponse, status_code=status.HTTP_201_CREATED)
async def create_summer_vacation(
    summer_vacation_data: SummerVacationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new summer vacation."""
    vacation_dict = summer_vacation_data.model_dump()
    # Convert empty strings to None for optional fields
    if vacation_dict.get("vacation_plan") == "":
        vacation_dict["vacation_plan"] = None
    if vacation_dict.get("trip_plan") == "":
        vacation_dict["trip_plan"] = None
    
    new_summer_vacation = SummerVacation(
        **vacation_dict,
        user_id=current_user.id
    )
    
    db.add(new_summer_vacation)
    await db.commit()
    await db.refresh(new_summer_vacation)
    
    return new_summer_vacation


@router.put("/{summer_vacation_id}", response_model=SummerVacationResponse)
async def update_summer_vacation(
    summer_vacation_id: int,
    summer_vacation_data: SummerVacationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a summer vacation."""
    result = await db.execute(
        select(SummerVacation).where(and_(SummerVacation.id == summer_vacation_id, SummerVacation.user_id == current_user.id))
    )
    summer_vacation = result.scalar_one_or_none()
    
    if not summer_vacation:
        raise HTTPException(status_code=404, detail="Summer vacation not found")
    
    # Update fields - only update provided fields
    update_data = summer_vacation_data.model_dump(exclude_unset=True)
    # Convert empty strings to None for optional fields
    for field, value in update_data.items():
        if value == "":
            value = None
        setattr(summer_vacation, field, value)
    
    await db.commit()
    await db.refresh(summer_vacation)
    
    return summer_vacation


@router.delete("/{summer_vacation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_summer_vacation(
    summer_vacation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a summer vacation."""
    result = await db.execute(
        select(SummerVacation).where(and_(SummerVacation.id == summer_vacation_id, SummerVacation.user_id == current_user.id))
    )
    summer_vacation = result.scalar_one_or_none()
    
    if not summer_vacation:
        raise HTTPException(status_code=404, detail="Summer vacation not found")
    
    await db.delete(summer_vacation)
    await db.commit()
    
    return None

