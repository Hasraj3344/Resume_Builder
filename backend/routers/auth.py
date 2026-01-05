"""Authentication API endpoints."""

import os
import json
from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile
from sqlalchemy.orm import Session
from typing import Optional

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


@router.post("/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
async def register(
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...),
    phone: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    profile_pic: Optional[UploadFile] = File(None),
    resume: Optional[UploadFile] = File(None),
    parsed_data: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Register a new user with optional profile picture and resume.

    Creates a new user account with a free subscription plan.
    Accepts multipart/form-data with optional file uploads.
    """
    # Validate password length
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters"
        )

    # Save profile picture if provided
    profile_pic_path = None
    if profile_pic:
        # Create uploads directory if it doesn't exist
        os.makedirs("uploads/profile_pics", exist_ok=True)

        # Generate unique filename
        file_ext = os.path.splitext(profile_pic.filename)[1]
        profile_pic_filename = f"{email.replace('@', '_').replace('.', '_')}_profile{file_ext}"
        profile_pic_path = f"uploads/profile_pics/{profile_pic_filename}"

        # Save file
        with open(profile_pic_path, "wb") as f:
            content = await profile_pic.read()
            f.write(content)

    # Save resume if provided
    resume_file_path = None
    resume_text = None
    if resume:
        # Create uploads directory if it doesn't exist
        os.makedirs("uploads/resumes", exist_ok=True)

        # Generate unique filename
        file_ext = os.path.splitext(resume.filename)[1]
        resume_filename = f"{email.replace('@', '_').replace('.', '_')}_resume{file_ext}"
        resume_file_path = f"uploads/resumes/{resume_filename}"

        # Save file
        with open(resume_file_path, "wb") as f:
            content = await resume.read()
            f.write(content)

    # Parse the parsed_data JSON string
    parsed_data_dict = None
    if parsed_data:
        try:
            parsed_data_dict = json.loads(parsed_data)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid parsed_data JSON format"
            )

    # Register user with all data
    user = AuthService.register_user(
        db=db,
        email=email,
        password=password,
        full_name=full_name,
        phone=phone,
        address=address,
        profile_pic_path=profile_pic_path,
        resume_file_path=resume_file_path,
        resume_text=resume_text,
        resume_parsed_data=parsed_data_dict
    )

    # Create session and generate token (auto-login after registration)
    access_token, jti, expires_at = AuthService.create_user_session(db, user)

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_at=expires_at,
        user=UserResponse.model_validate(user)
    )


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
