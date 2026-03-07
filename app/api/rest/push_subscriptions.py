"""
Push subscription REST endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.device import DeviceSubscription
from app.services.push_notification_service import PushNotificationService
from app.schemas.device import DeviceSubscriptionCreate, DeviceSubscriptionResponse

router = APIRouter(prefix="/push-subscriptions", tags=["push-subscriptions"])


@router.post("", response_model=DeviceSubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    subscription_data: DeviceSubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Register a device subscription for push notifications."""
    # Validate subscription data
    subscription_dict = {
        "endpoint": subscription_data.endpoint,
        "keys": subscription_data.keys
    }
    
    if not PushNotificationService.validate_subscription(subscription_dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid subscription data"
        )
    
    # Check if subscription already exists for this endpoint
    result = await db.execute(
        select(DeviceSubscription).where(
            and_(
                DeviceSubscription.user_id == current_user.id,
                DeviceSubscription.endpoint == subscription_data.endpoint
            )
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        # Update existing subscription
        existing.p256dh = subscription_data.keys["p256dh"]
        existing.auth = subscription_data.keys["auth"]
        existing.user_agent = subscription_data.user_agent
        await db.commit()
        await db.refresh(existing)
        return existing
    
    # Create new subscription
    subscription = DeviceSubscription(
        user_id=current_user.id,
        endpoint=subscription_data.endpoint,
        p256dh=subscription_data.keys["p256dh"],
        auth=subscription_data.keys["auth"],
        user_agent=subscription_data.user_agent
    )
    
    db.add(subscription)
    await db.commit()
    await db.refresh(subscription)
    
    return subscription


@router.get("", response_model=List[DeviceSubscriptionResponse])
async def get_subscriptions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's device subscriptions."""
    result = await db.execute(
        select(DeviceSubscription).where(
            DeviceSubscription.user_id == current_user.id
        )
    )
    subscriptions = result.scalars().all()
    return subscriptions


@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subscription(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Unregister a device subscription."""
    result = await db.execute(
        select(DeviceSubscription).where(
            and_(
                DeviceSubscription.id == subscription_id,
                DeviceSubscription.user_id == current_user.id
            )
        )
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    await db.delete(subscription)
    await db.commit()
    
    return None




