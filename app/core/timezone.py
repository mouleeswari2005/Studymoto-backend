"""
Timezone utilities for consistent IST (GMT+05:30) handling throughout the platform.
"""
from datetime import datetime, timezone, timedelta
import pytz
from typing import Optional

# IST timezone object
IST = pytz.timezone('Asia/Kolkata')

def now_ist() -> datetime:
    """Get current datetime in IST timezone."""
    return datetime.now(IST)

def utcnow_ist() -> datetime:
    """Get current UTC datetime but return as IST timezone-aware."""
    return datetime.now(timezone.utc).astimezone(IST)

def make_naive_ist(dt: Optional[datetime]) -> Optional[datetime]:
    """Convert timezone-aware datetime to naive datetime in IST."""
    if dt is None:
        return None
    if dt.tzinfo is not None:
        # Convert to IST and remove timezone info
        return dt.astimezone(IST).replace(tzinfo=None)
    return dt

def make_timezone_aware_ist(dt: Optional[datetime]) -> Optional[datetime]:
    """Convert naive datetime to IST timezone-aware datetime."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        # Assume the naive datetime is already in IST and add timezone info
        return IST.localize(dt)
    return dt.astimezone(IST)

def get_today_ist_date() -> datetime.date:
    """Get today's date in IST timezone."""
    return now_ist().date()

def get_current_hour_ist() -> int:
    """Get current hour in IST timezone."""
    return now_ist().hour

def format_datetime_ist(dt: Optional[datetime], format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime in IST timezone."""
    if dt is None:
        return ""
    ist_dt = make_timezone_aware_ist(dt)
    return ist_dt.strftime(format_str)

def parse_datetime_ist(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """Parse datetime string and return as IST timezone-aware datetime."""
    naive_dt = datetime.strptime(date_str, format_str)
    return IST.localize(naive_dt)

def get_start_of_day_ist(target_date: Optional[datetime.date] = None) -> datetime:
    """Get start of day (00:00:00) in IST for the given date."""
    if target_date is None:
        target_date = get_today_ist_date()
    return IST.localize(datetime.combine(target_date, datetime.min.time()))

def get_end_of_day_ist(target_date: Optional[datetime.date] = None) -> datetime:
    """Get end of day (23:59:59.999999) in IST for the given date."""
    if target_date is None:
        target_date = get_today_ist_date()
    return IST.localize(datetime.combine(target_date, datetime.max.time()))
