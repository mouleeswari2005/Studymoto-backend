"""
User preferences REST endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.preference import UserPreference
from app.schemas.preference import UserPreferenceCreate, UserPreferenceUpdate, UserPreferenceResponse

router = APIRouter(prefix="/preferences", tags=["preferences"])


@router.get("", response_model=UserPreferenceResponse)
async def get_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user preferences."""
    try:
        result = await db.execute(
            select(UserPreference).where(UserPreference.user_id == current_user.id)
        )
        preferences = result.scalar_one_or_none()
        
        if not preferences:
            # Create default preferences if they don't exist
            try:
                preferences = UserPreference(user_id=current_user.id)
                db.add(preferences)
                await db.commit()
                await db.refresh(preferences)
            except Exception as e:
                # If creation fails (e.g., missing columns), try to rollback and return defaults
                await db.rollback()
                import logging
                logging.warning(f"Could not create preferences, may need migration: {str(e)}")
                # Return a minimal preferences object with defaults
                from app.schemas.preference import UserPreferenceResponse
                return UserPreferenceResponse(
                    id=0,
                    user_id=current_user.id,
                    default_calendar_view="week",
                    time_format="12h",
                    timezone="Asia/Kolkata",
                    week_start_day=0,
                    email_notifications_enabled="true",
                    push_notifications_enabled="true",
                    study_duration_minutes=25,
                    short_break_duration_minutes=5,
                    long_break_duration_minutes=15
                )
        
        return preferences
    except Exception as e:
        import logging
        logging.error(f"Error getting preferences: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving preferences: {str(e)}"
        )


@router.put("", response_model=UserPreferenceResponse)
async def update_preferences(
    preference_data: UserPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user preferences."""
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == current_user.id)
    )
    preferences = result.scalar_one_or_none()
    
    if not preferences:
        # Create preferences if they don't exist
        create_data = preference_data.model_dump(exclude_unset=True)
        preferences = UserPreference(user_id=current_user.id, **create_data)
        db.add(preferences)
    else:
        # Update existing preferences
        update_data = preference_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(preferences, field, value)
    
    await db.commit()
    await db.refresh(preferences)
    
    return preferences

