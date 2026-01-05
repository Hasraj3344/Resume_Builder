"""Dependency injection functions for FastAPI."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from backend.database import get_db
from backend.config import settings
from backend.models.user import User
from backend.models.session import Session as SessionModel

# HTTP Bearer token scheme - auto_error=False to handle missing tokens ourselves
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.

    Args:
        credentials: HTTP Authorization credentials
        db: Database session

    Returns:
        User: Current authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Check if credentials were provided
    if credentials is None:
        print("[AUTH DEBUG] No Authorization header provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        token = credentials.credentials
        print(f"[AUTH DEBUG] Validating token: {token[:20]}...")

        # Decode JWT token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        user_id: str = payload.get("sub")
        token_jti: str = payload.get("jti")
        print(f"[AUTH DEBUG] Token decoded - user_id: {user_id}, jti: {token_jti}")

        if user_id is None or token_jti is None:
            print("[AUTH DEBUG] Missing user_id or jti in token")
            raise credentials_exception

    except JWTError as e:
        print(f"[AUTH DEBUG] JWT decode error: {e}")
        raise credentials_exception

    # Check if session exists and is not revoked
    session = db.query(SessionModel).filter(
        SessionModel.token_jti == token_jti,
        SessionModel.revoked == False
    ).first()

    if not session:
        print(f"[AUTH DEBUG] Session not found or revoked for jti: {token_jti}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has been revoked or expired"
        )

    print(f"[AUTH DEBUG] Session valid, fetching user {user_id}")

    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()

    if user is None or not user.is_active:
        print(f"[AUTH DEBUG] User not found or inactive: {user_id}")
        raise credentials_exception

    print(f"[AUTH DEBUG] Authentication successful for user: {user.email}")
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user.

    Args:
        current_user: Current user from token

    Returns:
        User: Current active user

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    return current_user
