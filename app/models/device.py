"""
Device subscription model for push notifications.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class DeviceSubscription(Base):
    """Device subscription model for push notifications."""
    __tablename__ = "device_subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    endpoint = Column(Text, nullable=False)  # Push subscription endpoint
    p256dh = Column(Text, nullable=False)  # Public key
    auth = Column(Text, nullable=False)  # Auth secret
    user_agent = Column(String, nullable=True)  # Browser/device info
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="device_subscriptions")




