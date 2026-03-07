"""
Push notification service for sending Web Push notifications.
"""
import json
import logging
from typing import Optional
from pywebpush import webpush, WebPushException
from app.core.config import settings
from app.models.device import DeviceSubscription

logger = logging.getLogger(__name__)


class PushNotificationService:
    """Service for sending push notifications."""
    
    @staticmethod
    def get_vapid_claims():
        """Get VAPID claims for push notifications."""
        if not settings.VAPID_PUBLIC_KEY or not settings.VAPID_PRIVATE_KEY:
            logger.warning("VAPID keys not configured. Push notifications will not work.")
            return None
        
        # Extract origin from endpoint (for aud claim)
        # The aud claim should be the origin of the push service
        # For most push services, this is the endpoint's origin
        return {
            "sub": settings.VAPID_EMAIL or "mailto:mouleeswarimurugan@gmail.com",
            "publicKey": settings.VAPID_PUBLIC_KEY,
            "privateKey": settings.VAPID_PRIVATE_KEY
        }
    
    @staticmethod
    def send_push_notification(
        subscription: DeviceSubscription,
        title: str,
        message: str,
        action_url: Optional[str] = None,
        notification_type: Optional[str] = None
    ) -> bool:
        """Send a push notification to a device subscription."""
        vapid_claims = PushNotificationService.get_vapid_claims()
        if not vapid_claims:
            logger.error("Cannot send push notification: VAPID keys not configured")
            return False
        
        try:
            # Prepare subscription info
            subscription_info = {
                "endpoint": subscription.endpoint,
                "keys": {
                    "p256dh": subscription.p256dh,
                    "auth": subscription.auth
                }
            }
            
            # Prepare notification payload
            payload = {
                "title": title,
                "body": message,
                "icon": "/vite.svg",  # Default icon, can be customized
                "badge": "/vite.svg",
                "data": {
                    "url": action_url or "/",
                    "type": notification_type
                }
            }
            
            # Extract origin from endpoint for aud claim
            from urllib.parse import urlparse
            endpoint_url = urlparse(subscription.endpoint)
            aud = f"{endpoint_url.scheme}://{endpoint_url.netloc}"
            
            # Send push notification
            webpush(
                subscription_info=subscription_info,
                data=json.dumps(payload),
                vapid_private_key=vapid_claims["privateKey"],
                vapid_claims={
                    "sub": vapid_claims["sub"],
                    "aud": aud
                }
            )
            
            logger.info(f"Push notification sent successfully to user {subscription.user_id}")
            return True
            
        except WebPushException as e:
            logger.error(f"Failed to send push notification: {e}")
            # Check if subscription is invalid (410 status)
            if hasattr(e, 'response') and e.response and e.response.status_code == 410:
                logger.warning(f"Subscription expired for user {subscription.user_id}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending push notification: {e}")
            return False
    
    @staticmethod
    def validate_subscription(subscription_data: dict) -> bool:
        """Validate a push subscription data structure."""
        required_fields = ["endpoint", "keys"]
        if not all(field in subscription_data for field in required_fields):
            return False
        
        if "keys" not in subscription_data:
            return False
        
        keys = subscription_data["keys"]
        if not isinstance(keys, dict):
            return False
        
        required_keys = ["p256dh", "auth"]
        if not all(key in keys for key in required_keys):
            return False
        
        return True




