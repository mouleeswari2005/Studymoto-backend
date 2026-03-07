"""
Classes REST endpoints.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.academic import Class, Term
from app.schemas.academic import ClassCreate, ClassUpdate, ClassResponse

router = APIRouter(prefix="/classes", tags=["classes"])


@router.get("", response_model=List[ClassResponse])
async def get_classes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    term_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's classes."""
    query = select(Class).where(Class.user_id == current_user.id)
    
    if term_id:
        query = query.where(Class.term_id == term_id)
    
    query = query.order_by(Class.name.asc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    classes = result.scalars().all()
    return classes


@router.get("/{class_id}", response_model=ClassResponse)
async def get_class(
    class_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific class."""
    result = await db.execute(
        select(Class).where(and_(Class.id == class_id, Class.user_id == current_user.id))
    )
    class_obj = result.scalar_one_or_none()
    
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    
    return class_obj


@router.post("", response_model=ClassResponse, status_code=status.HTTP_201_CREATED)
async def create_class(
    class_data: ClassCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new class."""
    # Verify term belongs to user if provided
    if class_data.term_id:
        result = await db.execute(
            select(Term).where(and_(Term.id == class_data.term_id, Term.user_id == current_user.id))
        )
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Term not found")
    
    new_class = Class(
        **class_data.model_dump(),
        user_id=current_user.id
    )
    
    db.add(new_class)
    await db.commit()
    await db.refresh(new_class)
    
    return new_class


@router.put("/{class_id}", response_model=ClassResponse)
async def update_class(
    class_id: int,
    class_data: ClassUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a class."""
    result = await db.execute(
        select(Class).where(and_(Class.id == class_id, Class.user_id == current_user.id))
    )
    class_obj = result.scalar_one_or_none()
    
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # Verify term if updating
    if class_data.term_id:
        result = await db.execute(
            select(Term).where(and_(Term.id == class_data.term_id, Term.user_id == current_user.id))
        )
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Term not found")
    
    # Update fields
    update_data = class_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(class_obj, field, value)
    
    await db.commit()
    await db.refresh(class_obj)
    
    return class_obj


@router.delete("/{class_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_class(
    class_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a class."""
    result = await db.execute(
        select(Class).where(and_(Class.id == class_id, Class.user_id == current_user.id))
    )
    class_obj = result.scalar_one_or_none()
    
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    
    await db.delete(class_obj)
    await db.commit()
    
    return None

