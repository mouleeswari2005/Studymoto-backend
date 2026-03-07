"""
Device subscription schemas.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class DeviceSubscriptionCreate(BaseModel):
    """Device subscription creation schema."""
    endpoint: str
    keys: dict  # Contains p256dh and auth
    user_agent: Optional[str] = None


class DeviceSubscriptionResponse(BaseModel):
    """Device subscription response schema."""
    id: int
    user_id: int
    endpoint: str
    user_agent: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True




