"""
FastAPI dependencies for authentication and authorization.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User, UserRole

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get the current authenticated user."""
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_type = payload.get("type")
    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id_str: Optional[str] = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    
    # Convert string user_id back to int for database query
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    
    return user


async def require_role(
    *allowed_roles: UserRole,
    current_user: User = Depends(get_current_user)
) -> User:
    """Require user to have one of the specified roles."""
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    return current_user


# Convenience dependencies for common role checks
async def require_student(current_user: User = Depends(get_current_user)) -> User:
    """Require user to be a student."""
    return await require_role(UserRole.STUDENT, current_user=current_user)


async def require_parent(current_user: User = Depends(get_current_user)) -> User:
    """Require user to be a parent."""
    return await require_role(UserRole.PARENT, current_user=current_user)


async def require_educator(current_user: User = Depends(get_current_user)) -> User:
    """Require user to be an educator."""
    return await require_role(UserRole.EDUCATOR, current_user=current_user)


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require user to be an admin."""
    return await require_role(UserRole.ADMIN, current_user=current_user)


async def require_premium(current_user: User = Depends(get_current_user)) -> User:
    """Require user to have premium access."""
    if not current_user.is_premium:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Premium feature - upgrade required",
        )
    return current_user

