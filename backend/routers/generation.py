"""
Generation API Router - Endpoints for resume optimization
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel
import sys
from pathlib import Path
import json

# Add parent directory to import src.models
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ..database import get_db
from ..dependencies import get_current_user
from ..models.user import User
from ..models.resume import Resume as ResumeDB
from ..services.resume_service import ResumeService
from ..services.jd_service import JDService
from ..services.matching_service import MatchingService
from ..services.generation_service import GenerationService
from ..services.usage_service import UsageService
from src.models import Resume, JobDescription, Certification

router = APIRouter()

resume_service = ResumeService()
jd_service = JDService()
matching_service = MatchingService()
generation_service = GenerationService()


class ManualGenerationRequest(BaseModel):
    job_description: str
    resume_id: Optional[int] = None


class OptimizeRequest(BaseModel):
    job_description: str
    match_results: Optional[Dict[str, Any]] = None


class AdzunaGenerationRequest(BaseModel):
    job_data: Dict[str, Any]  # Full job object from Adzuna search


def dict_to_resume(data: Dict[str, Any]) -> Resume:
    """Convert dictionary to Resume object"""
    from src.models import (
        ContactInfo, Education, Experience, Project
    )

    resume = Resume()

    # Contact Info - handle multiple formats robustly
    contact_data = data.get("contact_info") or data.get("contact")
    if contact_data:
        try:
            # If it's already a ContactInfo object, use it
            if isinstance(contact_data, ContactInfo):
                resume.contact = contact_data
            # If it's a dict, convert it
            elif isinstance(contact_data, dict):
                resume.contact = ContactInfo(
                    full_name=contact_data.get("name") or contact_data.get("full_name") or "Unknown",
                    email=contact_data.get("email"),
                    phone=contact_data.get("phone"),
                    location=contact_data.get("location"),
                    linkedin=contact_data.get("linkedin"),
                    github=contact_data.get("github")
                )
            # Fallback for other types (tuple, list, etc.)
            else:
                resume.contact = ContactInfo(
                    full_name="Unknown",
                    email=None,
                    phone=None,
                    location=None,
                    linkedin=None,
                    github=None
                )
        except Exception as e:
            # If all else fails, create minimal contact
            resume.contact = ContactInfo(
                full_name="Unknown",
                email=None,
                phone=None,
                location=None,
                linkedin=None,
                github=None
            )
    else:
        # No contact info provided
        resume.contact = ContactInfo(
            full_name="Unknown",
            email=None,
            phone=None,
            location=None,
            linkedin=None,
            github=None
        )

    # Professional Summary
    resume.summary = data.get("professional_summary") or data.get("summary") or ""

    # Education - with error handling
    education_list = []
    for edu in data.get("education", []):
        try:
            if isinstance(edu, dict):
                education_list.append(Education(
                    institution=edu.get("institution") or "Unknown",
                    degree=edu.get("degree"),
                    field_of_study=edu.get("field_of_study"),
                    graduation_date=edu.get("graduation_date"),
                    gpa=str(edu.get("gpa")) if edu.get("gpa") is not None else None,
                    location=edu.get("location")
                ))
        except Exception:
            continue  # Skip malformed education entries
    resume.education = education_list

    # Experience - with error handling
    experience_list = []
    for exp in data.get("experience", []):
        try:
            if isinstance(exp, dict):
                # Ensure bullets is a list
                bullets = exp.get("responsibilities") or exp.get("bullets", [])
                if not isinstance(bullets, list):
                    bullets = []

                experience_list.append(Experience(
                    company=exp.get("company") or "Unknown",
                    title=exp.get("job_title") or exp.get("title") or "Unknown",
                    location=exp.get("location"),
                    start_date=exp.get("start_date"),
                    end_date=exp.get("end_date"),
                    bullets=bullets
                ))
        except Exception:
            continue  # Skip malformed experience entries
    resume.experience = experience_list

    # Projects - with error handling
    projects_list = []
    for proj in data.get("projects", []):
        try:
            if isinstance(proj, dict):
                # Ensure technologies is a list
                technologies = proj.get("technologies", [])
                if not isinstance(technologies, list):
                    technologies = []

                projects_list.append(Project(
                    name=proj.get("title") or proj.get("name") or "Untitled Project",
                    description=proj.get("description") or "",
                    technologies=technologies,
                    url=proj.get("link") or proj.get("url")
                ))
        except Exception:
            continue  # Skip malformed project entries
    resume.projects = projects_list

    # Skills - ensure they're lists
    skills = data.get("skills", [])
    resume.skills = skills if isinstance(skills, list) else []

    # Certifications - convert to Certification objects
    certifications_data = data.get("certifications", [])
    certifications_list = []
    if isinstance(certifications_data, list):
        for cert in certifications_data:
            try:
                if isinstance(cert, str):
                    # Simple string certification
                    certifications_list.append(Certification(name=cert))
                elif isinstance(cert, dict):
                    # Dict with name/issuer/date
                    certifications_list.append(Certification(
                        name=cert.get("name", ""),
                        issuer=cert.get("issuer", ""),
                        date=cert.get("date"),
                        credential_id=cert.get("credential_id"),
                        url=cert.get("url")
                    ))
                else:
                    # Already a Certification object
                    certifications_list.append(cert)
            except Exception:
                continue
    resume.certifications = certifications_list

    return resume


def dict_to_jd(data: Dict[str, Any]) -> JobDescription:
    """Convert dictionary to JobDescription object"""
    jd = JobDescription(
        job_title=data.get("job_title", ""),
        company=data.get("company"),
        location=data.get("location"),
        job_type=data.get("job_type"),
        salary_range=data.get("salary_range"),
        overview=data.get("overview"),
        responsibilities=data.get("responsibilities", []),
        required_skills=data.get("required_skills", []),
        preferred_skills=data.get("preferred_skills", []),
        technologies=data.get("technologies", []),
        keywords=data.get("keywords", []),
        years_of_experience=data.get("years_of_experience"),
        education_requirement=data.get("education_requirement"),
    )
    return jd


@router.post("/manual")
async def analyze_manual_jd(
    request: ManualGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Manual workflow Step 1: Analyze JD and return match results

    Request body:
    {
        "job_description": "Job description text..."
    }

    Returns match analysis with matched/missing skills and recommendations
    """
    try:
        # 1. Parse job description
        jd_data = jd_service.parse_job_description(request.job_description)
        jd = dict_to_jd(jd_data)

        # 2. Get user's resume
        if not current_user.resume_parsed_data:
            raise HTTPException(
                status_code=400,
                detail="No resume found. Please upload a resume first."
            )

        try:
            resume = dict_to_resume(current_user.resume_parsed_data)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse resume data: {str(e)}"
            )

        # 3. Calculate match score
        try:
            match_analysis = matching_service.calculate_match_score(resume, jd)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to calculate match score: {str(e)}"
            )

        # 4. Extract skills from nested structure
        keyword_match = match_analysis.get("keyword_match", {})
        matched_skills = keyword_match.get("matched_skills", [])
        missing_skills = keyword_match.get("missing_skills", [])

        # 5. Generate recommendations
        recommendations = []
        if missing_skills:
            missing_count = len(missing_skills)
            if missing_count > 0:
                recommendations.append(f"Add {missing_count} missing skills to improve your match score")
            if missing_count > 5:
                recommendations.append("Consider taking courses or gaining experience in the top missing skills")

        if match_analysis.get("overall_score", 0) < 70:
            recommendations.append("Your resume could benefit from optimization to better match this role")

        return {
            "overall_score": match_analysis.get("overall_score", 0),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "keyword_match": keyword_match,  # Include full keyword match details
            "semantic_match": match_analysis.get("semantic_match", {}),  # Include semantic details
            "recommendations": recommendations,
            "job_description": request.job_description  # Store for next step
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze job description: {str(e)}"
        )


@router.post("/optimize")
async def optimize_resume_endpoint(
    request: OptimizeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Manual workflow Step 2: Optimize resume based on match results

    Request body:
    {
        "job_description": "Job description text...",
        "match_results": { ... }  # optional, from previous step
    }

    Returns optimized resume data and download URL
    """
    try:
        print("[OPTIMIZE] Starting resume optimization...")

        # 1. Check usage limits
        print("[OPTIMIZE] Checking usage limits...")
        can_generate, message, usage_info = UsageService.check_can_generate(db, str(current_user.id))

        if not can_generate:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "usage_limit_exceeded",
                    "message": message,
                    "usage_info": usage_info
                }
            )

        print(f"[OPTIMIZE] Usage check passed: {message}")

        # 2. Parse job description
        print("[OPTIMIZE] Parsing job description...")
        jd_data = jd_service.parse_job_description(request.job_description)
        jd = dict_to_jd(jd_data)
        print(f"[OPTIMIZE] JD parsed - {jd.job_title}")

        # 3. Get user's resume
        if not current_user.resume_parsed_data:
            raise HTTPException(
                status_code=400,
                detail="No resume found. Please upload a resume first."
            )

        print("[OPTIMIZE] Converting resume data...")
        resume = dict_to_resume(current_user.resume_parsed_data)
        print(f"[OPTIMIZE] Resume loaded - {resume.contact.full_name if resume.contact else 'Unknown'}")

        # 4. Calculate match score
        print("[OPTIMIZE] Calculating match score...")
        match_analysis = matching_service.calculate_match_score(resume, jd)
        print(f"[OPTIMIZE] Match score: {match_analysis.get('overall_score', 0):.1f}%")

        # 5. Optimize resume using LLM
        print("[OPTIMIZE] Calling LLM for optimization...")
        optimization_result = generation_service.optimize_resume(
            resume=resume,
            job_description=jd,
            workflow_type="manual"
        )
        print("[OPTIMIZE] LLM optimization complete")

        # 6. Export to DOCX
        print("[OPTIMIZE] Exporting to DOCX...")
        optimized_resume = dict_to_resume(optimization_result["optimized_resume"])
        docx_path = generation_service.export_to_docx(optimized_resume, user_id=str(current_user.id))
        print(f"[OPTIMIZE] DOCX exported to: {docx_path}")

        # 7. Save to database
        print("[OPTIMIZE] Saving to database...")
        resume_filename = current_user.resume_file_path.split("/")[-1] if current_user.resume_file_path else "resume.pdf"

        resume_record = ResumeDB(
            user_id=str(current_user.id),
            filename=resume_filename,
            resume_data=json.dumps(optimization_result["original_resume"]),
            job_description_data=json.dumps(jd_data),
            optimized_resume_data=json.dumps(optimization_result["optimized_resume"]),
            file_path=docx_path
        )
        db.add(resume_record)
        db.commit()
        db.refresh(resume_record)
        print(f"[OPTIMIZE] Saved to database with ID: {resume_record.id}")

        # 8. Increment usage counter
        print("[OPTIMIZE] Incrementing usage counter...")
        UsageService.increment_usage(db, str(current_user.id))
        updated_usage = UsageService.get_usage_stats(db, str(current_user.id))
        print(f"[OPTIMIZE] Usage updated: {updated_usage['used']}/{updated_usage['limit'] or 'unlimited'}")

        return {
            "id": resume_record.id,
            "optimized_resume": optimization_result["optimized_resume"],
            "match_analysis": {
                "keyword_match": match_analysis.get("keyword_match", {}),
                "semantic_match": match_analysis.get("semantic_match", {}),
                "overall_score": match_analysis.get("overall_score", 0)
            },
            "changes": optimization_result.get("changes", {}),
            "docx_filename": Path(docx_path).name,
            "download_url": f"/api/generation/download/{Path(docx_path).name}",
            "usage_info": updated_usage
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[OPTIMIZE ERROR] {type(e).__name__}: {str(e)}")
        print(f"[OPTIMIZE ERROR] Traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to optimize resume: {str(e)}"
        )


@router.post("/regenerate")
async def regenerate_resume(
    request: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """
    Regenerate DOCX with edited resume data

    Request body should contain the edited resume data
    """
    try:
        print(f"[REGENERATE] Starting for user: {current_user.email}")

        # Get edited resume data from request
        edited_resume_data = request.get("resume_data")
        if not edited_resume_data:
            raise HTTPException(
                status_code=400,
                detail="No resume data provided"
            )

        print("[REGENERATE] Converting edited resume to Resume object...")
        resume = dict_to_resume(edited_resume_data)
        print(f"[REGENERATE] Resume loaded - {resume.contact.full_name if resume.contact else 'Unknown'}")

        # Export to DOCX
        print("[REGENERATE] Exporting to DOCX...")
        docx_path = generation_service.export_to_docx(resume, user_id=str(current_user.id))
        print(f"[REGENERATE] DOCX exported to: {docx_path}")

        return {
            "id": f"resume_{current_user.id}_{Path(docx_path).stem}",
            "optimized_resume": edited_resume_data,
            "docx_filename": Path(docx_path).name,
            "download_url": f"/api/generation/download/{Path(docx_path).name}",
            "message": "Resume regenerated successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[REGENERATE ERROR] {type(e).__name__}: {str(e)}")
        print(f"[REGENERATE ERROR] Traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to regenerate resume: {str(e)}"
        )


@router.post("/adzuna")
async def optimize_for_adzuna_job(
    request: AdzunaGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Adzuna workflow: Optimize resume for a specific Adzuna job

    Request body:
    {
        "job_data": {
            "id": "1234567",
            "title": "Senior Data Engineer",
            "company": "Acme Corp",
            "location": "Remote",
            "description": "Full job description text...",
            "url": "https://www.adzuna.com/...",
            "salary_min": 120000,
            "salary_max": 180000
        }
    }

    Returns optimized resume + DOCX download link + match analysis
    """
    try:
        job_data = request.job_data
        print(f"[ADZUNA] Starting for user: {current_user.email}")
        print(f"[ADZUNA] Job: {job_data.get('title')} at {job_data.get('company')}")

        # 1. Check usage limits
        print("[ADZUNA] Checking usage limits...")
        can_generate, message, usage_info = UsageService.check_can_generate(db, str(current_user.id))

        if not can_generate:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "usage_limit_exceeded",
                    "message": message,
                    "usage_info": usage_info
                }
            )

        print(f"[ADZUNA] Usage check passed: {message}")

        # 2. Get user's resume
        if not current_user.resume_parsed_data:
            raise HTTPException(
                status_code=400,
                detail="No resume found. Please upload a resume first."
            )

        print("[ADZUNA] Converting resume data...")
        resume = dict_to_resume(current_user.resume_parsed_data)
        print(f"[ADZUNA] Resume loaded - {resume.contact.full_name if resume.contact else 'Unknown'}")

        # 3. Parse job description from Adzuna job data
        print("[ADZUNA] Parsing job description...")
        job_description_text = job_data.get("description", "")

        if not job_description_text:
            raise HTTPException(
                status_code=400,
                detail="Job description is empty"
            )

        jd_data = jd_service.parse_job_description(job_description_text)

        # Add job metadata to parsed JD
        jd_data["job_title"] = job_data.get("title", jd_data.get("job_title", ""))
        jd_data["company"] = job_data.get("company", jd_data.get("company"))
        jd_data["location"] = job_data.get("location", jd_data.get("location"))

        # Add salary info if available
        if job_data.get("salary_min") and job_data.get("salary_max"):
            jd_data["salary_range"] = f"${job_data['salary_min']:,} - ${job_data['salary_max']:,}"

        jd = dict_to_jd(jd_data)
        print(f"[ADZUNA] JD parsed - {jd.job_title} at {jd.company}")

        # 4. Calculate match score
        print("[ADZUNA] Calculating match score...")
        match_analysis = matching_service.calculate_match_score(resume, jd)
        print(f"[ADZUNA] Match score: {match_analysis.get('overall_score', 0):.1f}%")

        # 5. Optimize resume
        print("[ADZUNA] Calling LLM for optimization...")
        optimization_result = generation_service.optimize_resume(
            resume=resume,
            job_description=jd,
            workflow_type="adzuna"
        )
        print("[ADZUNA] LLM optimization complete")

        # 6. Export to DOCX
        print("[ADZUNA] Exporting to DOCX...")
        optimized_resume = dict_to_resume(optimization_result["optimized_resume"])

        # Use company name and job title in filename
        company_name = job_data.get("company", "company").replace(" ", "_").lower()
        job_title = job_data.get("title", "job").replace(" ", "_").lower()
        docx_filename = f"resume_{company_name}_{job_title}.docx"

        docx_path = generation_service.export_to_docx(
            optimized_resume,
            user_id=str(current_user.id),
            filename=docx_filename
        )
        print(f"[ADZUNA] DOCX exported to: {docx_path}")

        # 7. Save to database
        print("[ADZUNA] Saving to database...")
        resume_filename = current_user.resume_file_path.split("/")[-1] if current_user.resume_file_path else "resume.pdf"

        resume_record = ResumeDB(
            user_id=str(current_user.id),
            filename=f"adzuna_{job_data.get('id', 'job')}_{resume_filename}",
            resume_data=json.dumps(optimization_result["original_resume"]),
            job_description_data=json.dumps(jd_data),
            optimized_resume_data=json.dumps(optimization_result["optimized_resume"]),
            file_path=docx_path
        )
        db.add(resume_record)
        db.commit()
        db.refresh(resume_record)
        print(f"[ADZUNA] Saved to database with ID: {resume_record.id}")

        # 8. Increment usage counter
        print("[ADZUNA] Incrementing usage counter...")
        UsageService.increment_usage(db, str(current_user.id))
        updated_usage = UsageService.get_usage_stats(db, str(current_user.id))
        print(f"[ADZUNA] Usage updated: {updated_usage['used']}/{updated_usage['limit'] or 'unlimited'}")

        # 9. Return optimized resume + match analysis + download link
        return {
            "id": f"resume_{current_user.id}_adzuna_{job_data.get('id')}",
            "optimized_resume": optimization_result["optimized_resume"],
            "match_analysis": {
                "keyword_match": match_analysis.get("keyword_match", {}),
                "semantic_match": match_analysis.get("semantic_match", {}),
                "overall_score": match_analysis.get("overall_score", 0)
            },
            "job_info": {
                "id": job_data.get("id"),
                "title": job_data.get("title"),
                "company": job_data.get("company"),
                "location": job_data.get("location"),
                "url": job_data.get("url"),
                "salary_min": job_data.get("salary_min"),
                "salary_max": job_data.get("salary_max")
            },
            "docx_filename": Path(docx_path).name,
            "download_url": f"/api/generation/download/{Path(docx_path).name}",
            "usage_info": updated_usage
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[ADZUNA ERROR] {type(e).__name__}: {str(e)}")
        print(f"[ADZUNA ERROR] Traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to optimize resume for Adzuna job: {str(e)}"
        )


@router.get("/download/{filename}")
async def download_resume(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """
    Download generated DOCX resume
    """
    # Check both old (output/) and new (output/resumes/) locations
    file_path = Path("output/resumes") / filename

    if not file_path.exists():
        # Fallback to old location for backwards compatibility
        file_path = Path("output") / filename

    if not file_path.exists():
        print(f"[DOWNLOAD ERROR] File not found: {file_path}")
        print(f"[DOWNLOAD ERROR] Tried: output/resumes/{filename} and output/{filename}")
        raise HTTPException(status_code=404, detail=f"File not found: {filename}")

    print(f"[DOWNLOAD] Serving file: {file_path}")
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
