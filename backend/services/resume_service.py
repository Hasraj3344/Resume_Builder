"""
Resume Service - Integrates existing src/parsers/resume_parser.py
"""
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import UploadFile
import tempfile
import os

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.parsers.resume_parser import ResumeParser
from src.models import Resume


class ResumeService:
    """Service layer for resume operations using existing parsers"""

    def __init__(self):
        self.parser = ResumeParser()

    async def parse_resume(self, file: UploadFile) -> Dict[str, Any]:
        """
        Parse uploaded resume file and return structured data

        Args:
            file: UploadFile object (PDF or DOCX)

        Returns:
            Dictionary with parsed resume data
        """
        # Save uploaded file temporarily
        suffix = Path(file.filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        try:
            # Use existing resume parser
            resume: Resume = self.parser.parse(tmp_file_path)

            # Convert to dictionary using Pydantic's dict() method
            resume_dict = resume.dict()

            # Reformat to match frontend expectations
            parsed_data = {
                "contact_info": {
                    "name": resume_dict["contact"].get("full_name"),
                    "email": resume_dict["contact"].get("email"),
                    "phone": resume_dict["contact"].get("phone"),
                    "location": resume_dict["contact"].get("location"),
                    "linkedin": resume_dict["contact"].get("linkedin"),
                    "github": resume_dict["contact"].get("github"),
                },
                "professional_summary": resume_dict.get("summary"),
                "education": [
                    {
                        "institution": edu.get("institution"),
                        "degree": edu.get("degree"),
                        "field_of_study": edu.get("field_of_study"),
                        "graduation_date": edu.get("graduation_date"),
                        "gpa": edu.get("gpa"),
                        "location": edu.get("location"),
                    }
                    for edu in resume_dict.get("education", [])
                ],
                "experience": [
                    {
                        "company": exp.get("company"),
                        "job_title": exp.get("title"),
                        "location": exp.get("location"),
                        "start_date": exp.get("start_date"),
                        "end_date": exp.get("end_date"),
                        "responsibilities": exp.get("bullets", []),
                    }
                    for exp in resume_dict.get("experience", [])
                ],
                "projects": [
                    {
                        "title": proj.get("name"),
                        "description": proj.get("description"),
                        "technologies": proj.get("technologies", []),
                        "link": proj.get("url"),
                    }
                    for proj in resume_dict.get("projects", [])
                ],
                "skills": resume_dict.get("skills", []),
                "certifications": [cert.get("name") for cert in resume_dict.get("certifications", [])],
            }

            return parsed_data

        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)

    def get_resume_text(self, file_path: str) -> str:
        """Extract plain text from resume"""
        return self.parser.extract_text(file_path)

    def parse_resume_from_path(self, file_path: str) -> Dict[str, Any]:
        """
        Parse resume file from file system path

        Args:
            file_path: Path to resume file on disk

        Returns:
            Dictionary with parsed resume data
        """
        try:
            # Use existing resume parser
            resume: Resume = self.parser.parse(file_path)

            # Convert to dictionary using Pydantic's dict() method
            resume_dict = resume.dict()

            # Reformat to match frontend expectations
            parsed_data = {
                "contact_info": {
                    "name": resume_dict["contact"].get("full_name"),
                    "email": resume_dict["contact"].get("email"),
                    "phone": resume_dict["contact"].get("phone"),
                    "location": resume_dict["contact"].get("location"),
                    "linkedin": resume_dict["contact"].get("linkedin"),
                    "github": resume_dict["contact"].get("github"),
                },
                "professional_summary": resume_dict.get("summary"),
                "education": [
                    {
                        "institution": edu.get("institution"),
                        "degree": edu.get("degree"),
                        "field_of_study": edu.get("field_of_study"),
                        "graduation_date": edu.get("graduation_date"),
                        "gpa": edu.get("gpa"),
                        "location": edu.get("location"),
                    }
                    for edu in resume_dict.get("education", [])
                ],
                "experience": [
                    {
                        "company": exp.get("company"),
                        "job_title": exp.get("title"),
                        "location": exp.get("location"),
                        "start_date": exp.get("start_date"),
                        "end_date": exp.get("end_date"),
                        "responsibilities": exp.get("bullets", []),
                    }
                    for exp in resume_dict.get("experience", [])
                ],
                "projects": [
                    {
                        "title": proj.get("name"),
                        "description": proj.get("description"),
                        "technologies": proj.get("technologies", []),
                        "link": proj.get("url"),
                    }
                    for proj in resume_dict.get("projects", [])
                ],
                "skills": resume_dict.get("skills", []),
                "certifications": [cert.get("name") for cert in resume_dict.get("certifications", [])],
            }

            return parsed_data

        except Exception as e:
            raise Exception(f"Failed to parse resume: {str(e)}")
