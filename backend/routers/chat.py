"""Chat endpoints for resume Q&A."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.dependencies import get_current_user
from backend.models.user import User
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sys
from pathlib import Path

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.chat.chat_service import ChatService
from src.models import Resume, JobDescription

router = APIRouter()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    question: str
    resume: Optional[Dict[str, Any]] = None
    job_description: Optional[str] = None
    conversation_history: List[ChatMessage] = []


class ChatResponse(BaseModel):
    answer: str
    context_used: bool


@router.post("/ask", response_model=ChatResponse)
async def ask_question(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ask a question about the resume and/or job description

    Uses the existing ChatService from src/chat/chat_service.py
    """
    try:
        print(f"[CHAT] Question from {current_user.email}: {request.question}")

        # Convert resume dict to Resume object if provided
        resume = None
        if request.resume:
            resume = _dict_to_resume(request.resume)
            print(f"[CHAT] Resume provided: {resume.contact.full_name if resume.contact else 'Unknown'}")
        elif current_user.resume_parsed_data:
            # Use user's stored resume if not provided
            resume = _dict_to_resume(current_user.resume_parsed_data)
            print(f"[CHAT] Using stored resume")

        if not resume:
            raise HTTPException(
                status_code=400,
                detail="No resume available. Please upload a resume first."
            )

        # Parse job description if provided
        job_description = None
        if request.job_description:
            try:
                from src.parsers.jd_parser import JDParser
                jd_parser = JDParser()
                job_description = jd_parser.parse_text(request.job_description)
                print(f"[CHAT] Job description parsed: {job_description.job_title}")
            except Exception as e:
                print(f"[CHAT] JD parsing failed: {str(e)}, continuing without JD context")

        # Initialize chat service with resume (required) and optional JD
        print(f"[CHAT] Initializing ChatService...")
        chat_service = ChatService(
            resume=resume,
            jd=job_description
        )
        print(f"[CHAT] ChatService initialized successfully")

        # Get answer from chat service
        answer = chat_service.ask(request.question)

        print(f"[CHAT] Answer generated ({len(answer)} chars)")

        return ChatResponse(
            answer=answer,
            context_used=resume is not None or job_description is not None
        )

    except Exception as e:
        import traceback
        print(f"[CHAT ERROR] {str(e)}")
        print(f"[CHAT ERROR] Traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get answer: {str(e)}"
        )


def _dict_to_resume(data: Dict[str, Any]) -> Resume:
    """Convert resume dict to Resume object (simplified version)"""
    from src.models import Resume, ContactInfo, Experience, Education, Project

    resume = Resume(
        contact=ContactInfo(
            full_name=data.get("contact_info", {}).get("name") or data.get("contact_info", {}).get("full_name") or "Unknown",
            email=data.get("contact_info", {}).get("email"),
            phone=data.get("contact_info", {}).get("phone"),
            location=data.get("contact_info", {}).get("location"),
            linkedin=data.get("contact_info", {}).get("linkedin"),
            github=data.get("contact_info", {}).get("github")
        ) if data.get("contact_info") else None,
        summary=data.get("professional_summary") or data.get("summary", ""),
        skills=data.get("skills", []),
        experience=[],
        education=[],
        projects=[]
    )

    # Add experience
    for exp in data.get("experience", []):
        if isinstance(exp, dict):
            resume.experience.append(Experience(
                company=exp.get("company", "Unknown"),
                title=exp.get("job_title") or exp.get("title", "Unknown"),
                location=exp.get("location"),
                start_date=exp.get("start_date"),
                end_date=exp.get("end_date"),
                bullets=exp.get("responsibilities") or exp.get("bullets", [])
            ))

    # Add education
    for edu in data.get("education", []):
        if isinstance(edu, dict):
            resume.education.append(Education(
                institution=edu.get("institution", ""),
                degree=edu.get("degree", ""),
                field_of_study=edu.get("field_of_study"),
                graduation_date=edu.get("graduation_date"),
                gpa=str(edu.get("gpa")) if edu.get("gpa") else None
            ))

    return resume
