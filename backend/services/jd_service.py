"""
Job Description Service - Integrates existing src/parsers/jd_parser.py
"""
import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.parsers.jd_parser import JDParser
from src.models import JobDescription


class JDService:
    """Service layer for job description operations"""

    def __init__(self):
        self.parser = JDParser()

    def parse_job_description(self, jd_text: str) -> Dict[str, Any]:
        """
        Parse job description text and return structured data

        Args:
            jd_text: Raw job description text

        Returns:
            Dictionary with parsed JD data
        """
        # Use existing JD parser with parse_text method (not parse which expects a file path)
        jd: JobDescription = self.parser.parse_text(jd_text)

        # Convert to dictionary (matching actual JobDescription model fields)
        parsed_data = {
            "job_title": jd.job_title,
            "company": jd.company,
            "location": jd.location,
            "job_type": jd.job_type,
            "salary_range": jd.salary_range,
            "overview": jd.overview,
            "responsibilities": jd.responsibilities,
            "required_skills": jd.required_skills,
            "preferred_skills": jd.preferred_skills,
            "technologies": jd.technologies,
            "keywords": jd.keywords,
            "years_of_experience": jd.years_of_experience,
            "education_requirement": jd.education_requirement,
            "requirements": [req.dict() for req in jd.requirements] if jd.requirements else [],
        }

        return parsed_data
