"""Profile management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.dependencies import get_current_user
from backend.models.user import User
from backend.services.usage_service import UsageService
import os
from pathlib import Path

router = APIRouter()


@router.post("/upload-picture")
async def upload_profile_picture(
    profile_pic: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload profile picture for authenticated user
    """
    print(f"[PROFILE PIC] Received request from user: {current_user.email}")
    print(f"[PROFILE PIC] File info - name: {profile_pic.filename}, type: {profile_pic.content_type}")

    # Validate file type
    allowed_types = ["image/jpeg", "image/jpg", "image/png"]
    if profile_pic.content_type not in allowed_types:
        print(f"[PROFILE PIC ERROR] Invalid content type: {profile_pic.content_type}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{profile_pic.content_type}'. Only JPEG and PNG are allowed."
        )

    # Validate file size (2MB max)
    profile_pic.file.seek(0, 2)
    file_size = profile_pic.file.tell()
    profile_pic.file.seek(0)

    if file_size > 2 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds 2MB limit."
        )

    try:
        # Save file in user-specific directory with original filename
        user_profile_dir = os.path.join("uploads", "profile_pics", str(current_user.id))
        os.makedirs(user_profile_dir, exist_ok=True)

        # Keep original filename
        profile_pic_filename = profile_pic.filename
        profile_pic_path = os.path.join(user_profile_dir, profile_pic_filename)

        with open(profile_pic_path, "wb") as f:
            content = await profile_pic.read()
            f.write(content)

        print(f"[PROFILE PIC] Saved to: {profile_pic_path}")
        print(f"[PROFILE PIC] Original filename preserved: {profile_pic_filename}")

        # Update user profile_pic_path in database
        current_user.profile_pic_path = profile_pic_path
        db.commit()
        db.refresh(current_user)

        print(f"[PROFILE PIC] Database updated for user: {current_user.email}")

        # Return full user object
        user_data = {
            "id": str(current_user.id),
            "email": current_user.email,
            "full_name": current_user.full_name,
            "phone": current_user.phone,
            "address": current_user.address,
            "profile_pic_path": current_user.profile_pic_path,
            "resume_file_path": current_user.resume_file_path,
            "resume_parsed_data": current_user.resume_parsed_data,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
            "is_active": current_user.is_active,
        }

        return {
            "message": "Profile picture uploaded successfully",
            "user": user_data,
        }

    except Exception as e:
        import traceback
        print(f"[PROFILE PIC ERROR] {str(e)}")
        print(f"[PROFILE PIC ERROR] Traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload profile picture: {str(e)}"
        )


@router.put("/update")
async def update_profile(
    profile_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile information
    """
    try:
        # Update allowed fields
        if "full_name" in profile_data:
            current_user.full_name = profile_data["full_name"]
        if "phone" in profile_data:
            current_user.phone = profile_data["phone"]
        if "address" in profile_data:
            current_user.address = profile_data["address"]

        db.commit()
        db.refresh(current_user)

        # Return full user object
        user_data = {
            "id": str(current_user.id),
            "email": current_user.email,
            "full_name": current_user.full_name,
            "phone": current_user.phone,
            "address": current_user.address,
            "profile_pic_path": current_user.profile_pic_path,
            "resume_file_path": current_user.resume_file_path,
            "resume_parsed_data": current_user.resume_parsed_data,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
            "is_active": current_user.is_active,
        }

        return {
            "message": "Profile updated successfully",
            "user": user_data,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update profile: {str(e)}"
        )


@router.get("/usage")
async def get_usage_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's usage statistics

    Returns:
        - plan: "free" or "pro"
        - status: "active", "no_subscription", etc.
        - limit: Monthly resume generation limit (None for unlimited)
        - used: Number of resumes generated this month
        - remaining: Remaining resumes this month (None for unlimited)
        - reset_date: Date when usage resets (ISO format)
    """
    try:
        usage_stats = UsageService.get_usage_stats(db, str(current_user.id))
        return usage_stats
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get usage stats: {str(e)}"
        )
