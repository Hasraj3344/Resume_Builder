"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dependencies import get_current_user
from backend.models.user import User
from backend.schemas.auth import (
    UserRegister,
    UserLogin,
    LoginResponse,
    UserResponse,
    MessageResponse
)
from backend.services.auth_service import AuthService
from backend.utils.security import decode_token

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new user.

    Creates a new user account with a free subscription plan.
    """
    user = AuthService.register_user(
        db=db,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name
    )

    return user


@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login with email and password.

    Returns an access token and user information.
    """
    # Authenticate user
    user = AuthService.authenticate_user(
        db=db,
        email=credentials.email,
        password=credentials.password
    )

    # Create session and generate token
    access_token, jti, expires_at = AuthService.create_user_session(db, user)

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_at=expires_at,
        user=UserResponse.model_validate(user)
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout current user.

    Revokes all active sessions for the user.
    """
    # Revoke all user sessions
    AuthService.revoke_all_user_sessions(db, current_user.id)

    return MessageResponse(message="Successfully logged out")


@router.post("/logout-session", response_model=MessageResponse)
async def logout_session(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Logout a specific session by token.

    Revokes only the specific session token.
    """
    try:
        # Decode token to get JTI
        payload = decode_token(token)
        jti = payload.get("jti")

        if jti:
            AuthService.revoke_session(db, jti)
            return MessageResponse(message="Session revoked successfully")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information.
    """
    return current_user
