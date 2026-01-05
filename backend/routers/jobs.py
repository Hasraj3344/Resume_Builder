"""
Jobs API Router - Endpoints for Adzuna job search and matching
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from ..database import get_db
from ..dependencies import get_current_user
from ..models.user import User
from ..services.adzuna_service import AdzunaService
from ..services.matching_service import MatchingService

router = APIRouter()
adzuna_service = AdzunaService()
matching_service = MatchingService()


class JobSearchRequest(BaseModel):
    query: Optional[str] = None
    location: str
    filters: Optional[Dict[str, Any]] = None


class JobMatchRequest(BaseModel):
    resume_text: str
    jobs: List[Dict[str, Any]]


@router.get("/search")
async def search_jobs(
    query: Optional[str] = None,
    location: Optional[str] = None,
    experience_level: Optional[str] = None,
    work_mode: Optional[str] = None,
    page: int = 1,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Search for jobs using Adzuna API via query parameters
    Automatically matches jobs against user's resume if available

    Query params:
    - query: Job title or keywords (e.g., "data engineer")
    - location: Location (e.g., "Atlanta, GA", "Remote")
    - experience_level: Experience level (entry, mid, senior)
    - work_mode: Work mode (remote, onsite, hybrid)
    - page: Page number (default 1)

    Returns jobs with similarity_score field if resume is available
    """
    try:
        # Build filters dict
        filters = {}
        exclude_terms = []

        # Add experience level with proper inclusion and exclusion
        if experience_level:
            if not query:
                query = ""

            if experience_level == "entry":
                # Include: junior, entry level, intern
                query = f"{query} junior entry level intern".strip()
                # Exclude: senior, lead, manager
                exclude_terms.extend(["senior", "lead", "manager"])

            elif experience_level == "mid":
                # Include: intermediate, mid level
                query = f"{query} intermediate mid level".strip()
                # Exclude: junior, intern, senior
                exclude_terms.extend(["junior", "intern", "senior"])

            elif experience_level == "senior":
                # Include: senior, lead, head of
                query = f"{query} senior lead".strip()
                # Exclude: junior, entry, intern
                exclude_terms.extend(["junior", "entry", "intern"])

        # Handle work mode and location
        if work_mode == "remote":
            # Remote: set location to remote
            location = "remote"
        elif work_mode == "onsite":
            # On-Site: use provided location and exclude "remote" from results
            if not location or location.lower() == "united states":
                location = None  # Search all locations
            exclude_terms.append("remote")
        elif work_mode == "hybrid":
            # Hybrid: add hybrid to query
            query = f"{query} hybrid".strip() if query else "hybrid"
            if not location or location.lower() == "united states":
                location = None
        else:
            # No work mode filter
            if not location or location.lower() == "united states":
                location = None

        # Add exclusion terms to filters
        if exclude_terms:
            filters["what_exclude"] = " ".join(exclude_terms)

        # Search for jobs
        print(f"[JOBS] Searching Adzuna - query: '{query}', location: {location}, page: {page}, filters: {filters}")
        try:
            result = await adzuna_service.search_jobs(
                query=query,
                location=location,
                page=page,
                filters=filters
            )
            jobs = result["jobs"]
            total_count = result["count"]
            print(f"[JOBS] Adzuna returned {len(jobs)} jobs (total: {total_count})")
        except Exception as adzuna_error:
            import traceback
            print(f"[JOBS ERROR] Adzuna API error: {str(adzuna_error)}")
            print(f"[JOBS ERROR] Traceback:\n{traceback.format_exc()}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to search jobs: {str(adzuna_error)}"
            )

        # If user has a resume, match it against the jobs
        if current_user.resume_parsed_data and jobs:
            try:
                print(f"[JOBS] Attempting to match {len(jobs)} jobs against user's resume")
                # Extract resume text from parsed data
                resume_text = _extract_resume_text(current_user.resume_parsed_data)
                print(f"[JOBS] Extracted resume text length: {len(resume_text)}")

                # Match resume to jobs using vector similarity
                matched_jobs = matching_service.match_resume_to_jobs(
                    resume_text=resume_text,
                    job_descriptions=jobs
                )
                print(f"[JOBS] Matching complete, {len(matched_jobs)} jobs matched")

                # Sort by similarity score (highest first)
                matched_jobs.sort(key=lambda j: j.get('similarity_score', 0), reverse=True)

                return {
                    "jobs": matched_jobs,
                    "total": total_count,
                    "query": query,
                    "location": location,
                    "matched": True
                }
            except Exception as e:
                import traceback
                print(f"[JOBS] Resume matching failed: {str(e)}")
                print(f"[JOBS] Traceback:\n{traceback.format_exc()}")
                # Fall back to returning jobs without match scores
                pass

        return {
            "jobs": jobs,
            "total": total_count,
            "query": query,
            "location": location,
            "matched": False
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search jobs: {str(e)}"
        )


def _extract_resume_text(resume_data: Dict[str, Any]) -> str:
    """Extract text from resume data for matching"""
    text_parts = []

    # Professional summary
    if resume_data.get("professional_summary"):
        text_parts.append(resume_data["professional_summary"])

    # Skills
    if resume_data.get("skills"):
        skills = resume_data["skills"]
        if isinstance(skills, list):
            text_parts.append(" ".join(str(s) for s in skills))
        else:
            text_parts.append(str(skills))

    # Experience
    if resume_data.get("experience"):
        for exp in resume_data["experience"]:
            if isinstance(exp, dict):
                if exp.get("job_title"):
                    text_parts.append(exp["job_title"])
                if exp.get("responsibilities"):
                    resp = exp["responsibilities"]
                    if isinstance(resp, list):
                        text_parts.extend(str(r) for r in resp)
                    else:
                        text_parts.append(str(resp))

    # Projects
    if resume_data.get("projects"):
        for proj in resume_data["projects"]:
            if isinstance(proj, dict):
                if proj.get("description"):
                    text_parts.append(proj["description"])
                if proj.get("technologies"):
                    techs = proj["technologies"]
                    if isinstance(techs, list):
                        text_parts.append(" ".join(str(t) for t in techs))
                    else:
                        text_parts.append(str(techs))

    return " ".join(text_parts)


@router.post("/match")
async def match_resume_to_jobs(
    request: JobMatchRequest,
    current_user: User = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    """
    Match user's resume against job listings using FAISS vector search

    Request body:
    {
        "resume_text": "...",
        "jobs": [...]
    }

    Returns jobs sorted by match score
    """
    try:
        matched_jobs = matching_service.match_resume_to_jobs(
            resume_text=request.resume_text,
            job_descriptions=request.jobs
        )

        return matched_jobs
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to match jobs: {str(e)}"
        )


@router.get("/saved")
async def get_saved_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's saved/bookmarked jobs
    """
    # TODO: Query saved_jobs table
    return {
        "saved_jobs": [],
        "count": 0
    }


@router.post("/save")
async def save_job(
    job_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Save/bookmark a job
    """
    # TODO: Insert into saved_jobs table
    return {
        "message": "Job saved successfully",
        "job_id": job_data.get("id")
    }


@router.delete("/saved/{job_id}")
async def unsave_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove job from saved list
    """
    # TODO: Delete from saved_jobs table
    return {
        "message": "Job removed from saved list",
        "job_id": job_id
    }
