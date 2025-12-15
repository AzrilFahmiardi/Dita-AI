from typing import Optional, Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from database.models import User
from auth.security import verify_token

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    
    Args:
        credentials: The HTTP Bearer token credentials
        db: Database session
        
    Returns:
        The authenticated User object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    
    payload = verify_token(token, token_type="access")
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to ensure the current user is active.
    
    Args:
        current_user: The current authenticated user
        
    Returns:
        The active User object
        
    Raises:
        HTTPException: If user is not active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


def require_permission(permission_key: str) -> Callable:
    """
    Dependency factory to check if user has a specific permission.
    
    Args:
        permission_key: The permission key to check in role.permissions
        
    Returns:
        A dependency function that validates the permission
        
    Example:
        @app.get("/protected", dependencies=[Depends(require_permission("send_whatsapp"))])
    """
    async def permission_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if not current_user.role.permissions.get(permission_key, False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission_key} required"
            )
        return current_user
    
    return permission_checker


def require_role_level(max_level: int) -> Callable:
    """
    Dependency factory to check if user's role level is within allowed range.
    Lower level number means higher authority (KAPOLRI=1, KAPOLDA=2, KAPOLRES=3).
    
    Args:
        max_level: Maximum role level allowed (inclusive)
        
    Returns:
        A dependency function that validates the role level
        
    Example:
        @app.get("/admin-only", dependencies=[Depends(require_role_level(1))])
    """
    async def role_level_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if current_user.role.level > max_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient role level: {current_user.role.name} (level {current_user.role.level})"
            )
        return current_user
    
    return role_level_checker
