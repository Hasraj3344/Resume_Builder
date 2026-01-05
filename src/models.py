"""Pydantic models for structured resume and job description data."""

from typing import List, Optional, Dict, Any
from datetime import date
from pydantic import BaseModel, Field, EmailStr


class ContactInfo(BaseModel):
    """Contact information from resume."""
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None


class Experience(BaseModel):
    """Work experience entry."""
    company: str
    title: str
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None  # "Present" for current roles
    is_current: bool = False
    bullets: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "company": "Tech Corp",
                "title": "Software Engineer",
                "location": "San Francisco, CA",
                "start_date": "Jan 2022",
                "end_date": "Present",
                "is_current": True,
                "bullets": [
                    "Developed scalable microservices using Python and FastAPI",
                    "Reduced API response time by 40% through optimization"
                ],
                "technologies": ["Python", "FastAPI", "Docker", "AWS"]
            }
        }


class Education(BaseModel):
    """Education entry."""
    institution: str
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    location: Optional[str] = None
    graduation_date: Optional[str] = None
    gpa: Optional[str] = None
    honors: List[str] = Field(default_factory=list)
    relevant_coursework: List[str] = Field(default_factory=list)


class Project(BaseModel):
    """Project entry."""
    name: str
    description: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)
    bullets: List[str] = Field(default_factory=list)
    url: Optional[str] = None
    date: Optional[str] = None


class Certification(BaseModel):
    """Certification entry."""
    name: str
    issuer: Optional[str] = None
    date: Optional[str] = None
    credential_id: Optional[str] = None
    url: Optional[str] = None


class Resume(BaseModel):
    """Complete resume structure."""
    contact: ContactInfo = Field(default_factory=ContactInfo)
    summary: Optional[str] = None
    experience: List[Experience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    genai_skills: List[str] = Field(default_factory=list)  # Separate GenAI/ML skills section
    projects: List[Project] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)

    # Metadata
    raw_text: Optional[str] = None
    source_file: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "contact": {
                    "full_name": "John Doe",
                    "email": "john@example.com",
                    "phone": "+1-234-567-8900",
                    "linkedin": "linkedin.com/in/johndoe"
                },
                "summary": "Experienced software engineer with 5+ years...",
                "experience": [],
                "education": [],
                "skills": ["Python", "JavaScript", "AWS"],
                "projects": []
            }
        }


class JobRequirement(BaseModel):
    """Individual job requirement."""
    category: str  # "required", "preferred", "nice_to_have"
    description: str
    skills: List[str] = Field(default_factory=list)


class JobDescription(BaseModel):
    """Job description structure."""
    job_title: str
    company: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None  # "Full-time", "Contract", etc.
    salary_range: Optional[str] = None

    # Main sections
    overview: Optional[str] = None
    responsibilities: List[str] = Field(default_factory=list)
    requirements: List[JobRequirement] = Field(default_factory=list)

    # Extracted entities
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)

    # Experience requirements
    years_of_experience: Optional[str] = None
    education_requirement: Optional[str] = None

    # Metadata
    raw_text: Optional[str] = None
    source_file: Optional[str] = None
    url: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "job_title": "Senior Python Developer",
                "company": "Tech Startup Inc.",
                "location": "Remote",
                "overview": "We are seeking a skilled Python developer...",
                "responsibilities": [
                    "Design and implement scalable backend services",
                    "Collaborate with cross-functional teams"
                ],
                "required_skills": ["Python", "Django", "PostgreSQL"],
                "preferred_skills": ["AWS", "Docker", "CI/CD"],
                "years_of_experience": "5+",
                "education_requirement": "Bachelor's in Computer Science or equivalent"
            }
        }


class MatchResult(BaseModel):
    """Result of matching resume to job description."""
    overall_score: float = Field(ge=0.0, le=1.0)
    keyword_match_score: float = Field(ge=0.0, le=1.0)
    skill_match_score: float = Field(ge=0.0, le=1.0)
    experience_match_score: float = Field(ge=0.0, le=1.0)

    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    matched_keywords: List[str] = Field(default_factory=list)
    missing_keywords: List[str] = Field(default_factory=list)

    suggestions: List[str] = Field(default_factory=list)
    relevant_experiences: List[int] = Field(default_factory=list)  # Indices of relevant experience entries


class OptimizedResume(BaseModel):
    """Optimized resume output."""
    original_resume: Resume
    job_description: JobDescription
    match_result: MatchResult
    optimized_resume: Resume
    changes_made: List[str] = Field(default_factory=list)
    generation_timestamp: Optional[str] = None
