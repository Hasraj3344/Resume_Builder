"""
Generation Service - Integrates existing resume generator and DOCX exporter
"""
import sys
from pathlib import Path
from typing import Dict, Any
import tempfile
import os

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.generation.generator import ResumeGenerator
from src.generation.llm_service import get_default_llm_service
from src.export.docx_formatter import DOCXFormatter
from src.models import Resume, JobDescription


class GenerationService:
    """Service layer for resume generation and optimization"""

    def __init__(self):
        self.llm_service = get_default_llm_service()
        self.generator = ResumeGenerator(self.llm_service)
        self.docx_formatter = DOCXFormatter()

    def optimize_resume(
        self,
        resume: Resume,
        job_description: JobDescription,
        workflow_type: str = "manual"
    ) -> Dict[str, Any]:
        """
        Optimize resume for specific job description

        Args:
            resume: Parsed resume object
            job_description: Parsed JD object
            workflow_type: "manual" or "adzuna"

        Returns:
            Dictionary with optimized resume and metadata
        """
        # Use existing resume generator (method is called generate_optimized_resume, not optimize_resume)
        optimized_resume = self.generator.generate_optimized_resume(resume, job_description)

        # Generate comparison analysis
        comparison = self.generator.generate_comparison_report(
            resume,
            optimized_resume,
            job_description
        )

        result = {
            "original_resume": self._resume_to_dict(resume),
            "optimized_resume": self._resume_to_dict(optimized_resume),
            "comparison": comparison,
            "workflow_type": workflow_type,
        }

        return result

    def export_to_docx(self, resume: Resume, user_id: str = None, filename: str = None) -> str:
        """
        Export resume to DOCX format and return file path

        Args:
            resume: Resume object to export
            user_id: Optional user ID for filename
            filename: Optional custom filename (if not provided, auto-generated)

        Returns:
            Path to generated DOCX file
        """
        # Create output directory if it doesn't exist
        output_dir = Path("output/resumes")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Use custom filename if provided, otherwise generate one
        if filename:
            # Ensure it ends with .docx
            if not filename.endswith('.docx'):
                filename = f"{filename}.docx"
        else:
            # Generate filename with timestamp
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

            # Use contact name or user_id in filename
            name_part = "resume"
            if resume.contact:
                contact_name = getattr(resume.contact, 'full_name', None) or getattr(resume.contact, 'name', None)
                if contact_name:
                    # Sanitize filename
                    name_part = contact_name.replace(' ', '_').replace('/', '_')[:30]
            elif user_id:
                name_part = f"user_{user_id[:8]}"

            filename = f"{name_part}_optimized_{timestamp}.docx"

        output_path = str(output_dir / filename)

        # Use existing DOCX formatter
        self.docx_formatter.export_resume(resume, output_path)

        print(f"[EXPORT] Resume saved to: {output_path}")
        return output_path

    def _resume_to_dict(self, resume: Resume) -> Dict[str, Any]:
        """Convert Resume object to dictionary"""
        # Handle contact field (could be 'contact' or 'contact_info')
        contact = getattr(resume, 'contact', None) or getattr(resume, 'contact_info', None)

        return {
            "contact_info": {
                "name": contact.full_name if contact and hasattr(contact, 'full_name') else (contact.name if contact else None),
                "email": contact.email if contact else None,
                "phone": contact.phone if contact else None,
                "location": contact.location if contact else None,
                "linkedin": contact.linkedin if contact else None,
                "github": contact.github if contact else None,
            },
            "professional_summary": getattr(resume, 'summary', None) or getattr(resume, 'professional_summary', None),
            "education": [
                {
                    "institution": edu.institution,
                    "degree": edu.degree,
                    "field_of_study": edu.field_of_study,
                    "graduation_date": edu.graduation_date,
                    "gpa": edu.gpa,
                    "location": edu.location,
                }
                for edu in (resume.education or [])
            ],
            "experience": [
                {
                    "company": exp.company,
                    "job_title": getattr(exp, 'title', None) or getattr(exp, 'job_title', None),
                    "location": exp.location,
                    "start_date": exp.start_date,
                    "end_date": exp.end_date,
                    "responsibilities": getattr(exp, 'bullets', None) or getattr(exp, 'responsibilities', None) or [],
                }
                for exp in (resume.experience or [])
            ],
            "projects": [
                {
                    "title": getattr(proj, 'name', None) or getattr(proj, 'title', None),
                    "description": proj.description,
                    "technologies": proj.technologies or [],
                    "link": getattr(proj, 'url', None) or getattr(proj, 'link', None),
                }
                for proj in (resume.projects or [])
            ],
            "skills": resume.skills or [],
            "certifications": [
                {
                    "name": cert.name if hasattr(cert, 'name') else str(cert),
                    "issuer": cert.issuer if hasattr(cert, 'issuer') else None,
                    "date": cert.date if hasattr(cert, 'date') else None,
                    "credential_id": cert.credential_id if hasattr(cert, 'credential_id') else None,
                    "url": cert.url if hasattr(cert, 'url') else None,
                }
                for cert in (resume.certifications or [])
            ],
        }
