"""
Resume API Router - Endpoints for resume operations
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Body
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from ..database import get_db
from ..dependencies import get_current_user
from ..models.user import User
from ..services.resume_service import ResumeService

router = APIRouter()
resume_service = ResumeService()


# Pydantic models for resume editing
class ContactInfoUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None


class EducationUpdate(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    graduation_date: Optional[str] = None
    gpa: Optional[str] = None
    location: Optional[str] = None


class ExperienceUpdate(BaseModel):
    company: Optional[str] = None
    job_title: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    responsibilities: Optional[List[str]] = None


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    technologies: Optional[List[str]] = None
    link: Optional[str] = None


class ResumeEditRequest(BaseModel):
    contact_info: Optional[ContactInfoUpdate] = None
    professional_summary: Optional[str] = None
    education: Optional[List[EducationUpdate]] = None
    experience: Optional[List[ExperienceUpdate]] = None
    projects: Optional[List[ProjectUpdate]] = None
    skills: Optional[List[str]] = None
    certifications: Optional[List[str]] = None


@router.post("/parse")
async def parse_resume(
    resume: UploadFile = File(...),
) -> Dict[str, Any]:
    """
    Parse uploaded resume file (PDF or DOCX)
    Returns structured data: education, experience, skills, etc.

    This endpoint is used during registration (Step 2)
    """
    # Validate file type
    allowed_types = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    if resume.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only PDF and DOCX are allowed."
        )

    # Validate file size (5MB max)
    resume.file.seek(0, 2)  # Seek to end
    file_size = resume.file.tell()
    resume.file.seek(0)  # Reset to beginning

    if file_size > 5 * 1024 * 1024:  # 5MB
        raise HTTPException(
            status_code=400,
            detail="File size exceeds 5MB limit."
        )

    try:
        # Parse resume using existing parser
        parsed_data = await resume_service.parse_resume(resume)
        return parsed_data
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse resume: {str(e)}"
        )


@router.post("/upload")
async def upload_resume(
    resume: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload and parse resume for authenticated user
    Replaces existing resume data
    """
    import os

    print(f"[UPLOAD] Received request from user: {current_user.email}")
    print(f"[UPLOAD] File info - name: {resume.filename}, type: {resume.content_type}")

    # Validate file type
    allowed_types = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword"  # Added for older .doc files
    ]
    if resume.content_type not in allowed_types:
        print(f"[UPLOAD ERROR] Invalid content type: {resume.content_type}")
        print(f"[UPLOAD ERROR] Allowed types: {allowed_types}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{resume.content_type}'. Only PDF and DOCX are allowed."
        )

    # Validate file size (5MB max)
    resume.file.seek(0, 2)
    file_size = resume.file.tell()
    resume.file.seek(0)

    if file_size > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds 5MB limit."
        )

    try:
        # Save file in user-specific directory with original filename
        user_resume_dir = os.path.join("uploads", "resumes", str(current_user.id))
        os.makedirs(user_resume_dir, exist_ok=True)

        # Keep original filename
        resume_filename = resume.filename
        resume_file_path = os.path.join(user_resume_dir, resume_filename)

        with open(resume_file_path, "wb") as f:
            content = await resume.read()
            f.write(content)

        print(f"[UPLOAD] Resume saved to: {resume_file_path}")
        print(f"[UPLOAD] Original filename preserved: {resume_filename}")

        # Parse resume from saved file path with timeout protection
        print(f"[UPLOAD] Parsing resume from: {resume_file_path}")
        try:
            import asyncio
            from concurrent.futures import ThreadPoolExecutor

            # Add 60-second timeout for parsing (Python 3.8 compatible)
            # PDFs can take longer to process than DOCX files
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as pool:
                parsed_data = await asyncio.wait_for(
                    loop.run_in_executor(pool, resume_service.parse_resume_from_path, resume_file_path),
                    timeout=60.0
                )
            print(f"[UPLOAD] Resume parsed - Keys: {list(parsed_data.keys())}")
            print(f"[UPLOAD] Contact Info: {parsed_data.get('contact_info')}")
        except asyncio.TimeoutError:
            print(f"[UPLOAD ERROR] Resume parsing timed out after 60 seconds")
            raise HTTPException(
                status_code=500,
                detail="Resume parsing timed out. Your PDF may be too complex or corrupted. Try converting it to DOCX or using a different PDF."
            )
        except Exception as e:
            print(f"[UPLOAD ERROR] Resume parsing failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse resume: {str(e)}"
            )

        # Update user record
        current_user.resume_file_path = resume_file_path
        current_user.resume_parsed_data = parsed_data
        db.commit()
        db.refresh(current_user)

        print(f"[UPLOAD] Database updated for user: {current_user.email}")

        # Return full user object with all fields
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
            "message": "Resume uploaded and parsed successfully",
            "user": user_data,
            "parsed_data": parsed_data,
        }

    except Exception as e:
        import traceback
        print(f"[UPLOAD ERROR] {str(e)}")
        print(f"[UPLOAD ERROR] Traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload resume: {str(e)}"
        )


@router.get("/current")
async def get_current_resume(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's resume data
    """
    return {
        "user_id": current_user.id,
        "resume_file_path": current_user.resume_file_path,
        "parsed_data": current_user.resume_parsed_data,
    }


@router.put("/update")
async def update_resume(
    resume: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user's resume
    """
    # Validate and parse new resume
    parsed_data = await resume_service.parse_resume(resume)

    # TODO: Update database
    # - Save file to uploads/
    # - Update user.resume_file_path
    # - Update user.resume_parsed_data

    return {
        "message": "Resume updated successfully",
        "parsed_data": parsed_data
    }


@router.delete("/delete")
async def delete_resume(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete user's resume
    """
    # TODO: Delete from database and file system
    return {"message": "Resume deleted successfully"}


@router.put("/edit")
async def edit_resume(
    edit_request: ResumeEditRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Edit parsed resume data before analysis

    Allows users to modify contact info, education, experience, projects,
    skills, and certifications in the parsed resume data.
    """
    print(f"[RESUME EDIT] User {current_user.email} editing resume")

    # Get current parsed data
    if not current_user.resume_parsed_data:
        raise HTTPException(
            status_code=404,
            detail="No parsed resume data found. Please upload a resume first."
        )

    # Create a copy of current data
    import copy
    updated_data = copy.deepcopy(current_user.resume_parsed_data)

    # Update contact info
    if edit_request.contact_info:
        if 'contact_info' not in updated_data:
            updated_data['contact_info'] = {}

        if edit_request.contact_info.name is not None:
            updated_data['contact_info']['name'] = edit_request.contact_info.name
        if edit_request.contact_info.email is not None:
            updated_data['contact_info']['email'] = edit_request.contact_info.email
        if edit_request.contact_info.phone is not None:
            updated_data['contact_info']['phone'] = edit_request.contact_info.phone
        if edit_request.contact_info.location is not None:
            updated_data['contact_info']['location'] = edit_request.contact_info.location
        if edit_request.contact_info.linkedin is not None:
            updated_data['contact_info']['linkedin'] = edit_request.contact_info.linkedin
        if edit_request.contact_info.github is not None:
            updated_data['contact_info']['github'] = edit_request.contact_info.github

    # Update professional summary
    if edit_request.professional_summary is not None:
        updated_data['professional_summary'] = edit_request.professional_summary

    # Update education (replace entire array)
    if edit_request.education is not None:
        updated_data['education'] = [edu.dict(exclude_none=True) for edu in edit_request.education]

    # Update experience (replace entire array)
    if edit_request.experience is not None:
        updated_data['experience'] = [exp.dict(exclude_none=True) for exp in edit_request.experience]

    # Update projects (replace entire array)
    if edit_request.projects is not None:
        updated_data['projects'] = [proj.dict(exclude_none=True) for proj in edit_request.projects]

    # Update skills (replace entire array)
    if edit_request.skills is not None:
        updated_data['skills'] = edit_request.skills

    # Update certifications (replace entire array)
    if edit_request.certifications is not None:
        updated_data['certifications'] = edit_request.certifications

    # Save updated data to database
    current_user.resume_parsed_data = updated_data
    db.commit()
    db.refresh(current_user)

    print(f"[RESUME EDIT] Successfully updated resume for user {current_user.email}")

    return {
        "message": "Resume data updated successfully",
        "updated_data": updated_data
    }
