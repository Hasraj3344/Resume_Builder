"""Job Description parser."""

import re
from pathlib import Path
from typing import List, Dict, Optional
import pdfplumber
import docx2txt
from docx import Document

from src.models import JobDescription, JobRequirement


class JDParser:
    """Parser for Job Description documents."""

    # Common section headers in job descriptions
    SECTION_HEADERS = {
        'overview': ['overview', 'about', 'description', 'summary', 'about the role', 'about the position', 'job description', 'role description'],
        'responsibilities': ['responsibilities', 'duties', 'what you will do', 'what you\'ll do', 'key responsibilities', 'your responsibilities', 'job responsibilities', 'key duties', 'main responsibilities'],
        'requirements': ['requirements', 'qualifications', 'what we\'re looking for', 'what we are looking for', 'required qualifications', 'minimum qualifications', 'required skills', 'must have', 'essential skills', 'mandatory skills', 'required experience'],
        'preferred': ['preferred', 'nice to have', 'bonus', 'preferred qualifications', 'plus', 'desired', 'preferred skills', 'good to have', 'additional skills'],
        'benefits': ['benefits', 'what we offer', 'perks', 'compensation', 'salary', 'package'],
        'about_company': ['about us', 'about the company', 'company overview', 'who we are', 'company description']
    }

    # Common technical skills and tools (expanded for data engineering)
    COMMON_SKILLS = [
        # Programming Languages
        'python', 'java', 'javascript', 'typescript', 'scala', 'c++', 'c#', 'ruby', 'go', 'rust', 'php', 'r',
        # Web Frameworks
        'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'spring', 'fastapi',
        # Cloud Platforms
        'aws', 'azure', 'gcp', 'google cloud', 'azure cloud', 'amazon web services',
        # DevOps & Containers
        'docker', 'kubernetes', 'terraform', 'jenkins', 'ci/cd', 'ansible', 'gitlab', 'github actions',
        # Databases
        'sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'cassandra', 'dynamodb', 'cosmosdb',
        # Data Engineering & Big Data
        'spark', 'pyspark', 'apache spark', 'databricks', 'airflow', 'kafka', 'hadoop', 'hive', 'presto',
        'etl', 'elt', 'data pipeline', 'data pipelines', 'data warehouse', 'data lake', 'delta lake',
        'snowflake', 'redshift', 'bigquery', 'synapse', 'azure data factory', 'adf', 'glue',
        # BI & Analytics
        'tableau', 'power bi', 'looker', 'qlik', 'data visualization', 'data analysis', 'analytics',
        # ML & AI
        'machine learning', 'ml', 'ai', 'deep learning', 'nlp', 'computer vision', 'tensorflow', 'pytorch',
        'data science', 'scikit-learn', 'pandas', 'numpy',
        # Version Control & Collaboration
        'git', 'github', 'gitlab', 'bitbucket', 'agile', 'scrum', 'jira', 'confluence',
        # APIs & Architecture
        'rest', 'api', 'rest api', 'restful', 'microservices', 'graphql', 'soap',
        # Data Governance & Quality
        'data governance', 'data quality', 'data modeling', 'dimensional modeling', 'star schema',
        # Testing
        'pytest', 'junit', 'testing', 'unit testing', 'integration testing',
        # Web Technologies
        'html', 'css', 'sass', 'webpack', 'babel', 'jest'
    ]

    def __init__(self):
        """Initialize the JD parser."""
        pass

    def parse(self, file_path: str) -> JobDescription:
        """
        Parse a job description file into structured data.

        Args:
            file_path: Path to the JD file (can be .txt, .pdf, or .docx)

        Returns:
            JobDescription object with structured data
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Job description file not found: {file_path}")

        # Extract text based on file type
        if file_path.suffix.lower() == '.pdf':
            text = self._extract_text_from_pdf(str(file_path))
        elif file_path.suffix.lower() in ['.docx', '.doc']:
            text = self._extract_text_from_docx(str(file_path))
        elif file_path.suffix.lower() == '.txt':
            text = file_path.read_text(encoding='utf-8')
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

        # Parse the job description
        jd = self._parse_text(text)
        jd.raw_text = text
        jd.source_file = str(file_path)

        return jd

    def parse_text(self, text: str) -> JobDescription:
        """
        Parse job description from plain text.

        Args:
            text: Job description text

        Returns:
            JobDescription object
        """
        return self._parse_text(text)

    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            raise ValueError(f"Error extracting text from PDF: {e}")

        return text.strip()

    def _extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            text = docx2txt.process(file_path)
            if text and text.strip():
                return text.strip()

            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            raise ValueError(f"Error extracting text from DOCX: {e}")

    def _parse_text(self, text: str) -> JobDescription:
        """Parse job description text into structured data."""
        # Extract basic information
        job_title = self._extract_job_title(text)
        company = self._extract_company(text)
        location = self._extract_location(text)
        job_type = self._extract_job_type(text)

        # Identify sections
        sections = self._identify_sections(text)

        # Parse sections
        overview = sections.get('overview', '')
        responsibilities = self._extract_list_items(sections.get('responsibilities', ''))
        requirements_text = sections.get('requirements', '')
        preferred_text = sections.get('preferred', '')

        # Extract skills and keywords
        all_text = text.lower()
        required_skills = self._extract_skills(requirements_text)
        preferred_skills = self._extract_skills(preferred_text)
        technologies = list(set(required_skills + preferred_skills))
        keywords = self._extract_keywords(text)

        # Extract experience and education requirements
        years_of_experience = self._extract_years_of_experience(text)
        education_requirement = self._extract_education_requirement(text)

        # Parse requirements into structured format
        requirements = []
        if requirements_text:
            for item in self._extract_list_items(requirements_text):
                req = JobRequirement(
                    category="required",
                    description=item,
                    skills=self._extract_skills(item)
                )
                requirements.append(req)

        if preferred_text:
            for item in self._extract_list_items(preferred_text):
                req = JobRequirement(
                    category="preferred",
                    description=item,
                    skills=self._extract_skills(item)
                )
                requirements.append(req)

        return JobDescription(
            job_title=job_title,
            company=company,
            location=location,
            job_type=job_type,
            overview=overview,
            responsibilities=responsibilities,
            requirements=requirements,
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            technologies=technologies,
            keywords=keywords,
            years_of_experience=years_of_experience,
            education_requirement=education_requirement
        )

    def _identify_sections(self, text: str) -> Dict[str, str]:
        """Identify and extract different sections from JD text."""
        sections = {}
        lines = text.split('\n')
        current_section = None
        section_content = []

        for i, line in enumerate(lines):
            line_stripped = line.strip()
            line_lower = line_stripped.lower()

            # Skip empty lines at section boundaries
            if not line_stripped and not current_section:
                continue

            # Check if this line is a section header
            detected_section = None
            for section_name, headers in self.SECTION_HEADERS.items():
                for header in headers:
                    # Match if line is exactly the header or starts with it
                    # Be more flexible with matching
                    if line_lower == header:
                        detected_section = section_name
                        break
                    elif len(line_lower) < 60 and (
                        line_lower.startswith(header) or
                        header in line_lower and len(line_lower) < len(header) + 10
                    ):
                        detected_section = section_name
                        break
                if detected_section:
                    break

            # Also check for common patterns like "Job Responsibilities" or "Required Skills"
            if not detected_section and len(line_stripped) < 60:
                if re.match(r'^(Job\s+)?Responsibilities?[\s:]*$', line_stripped, re.IGNORECASE):
                    detected_section = 'responsibilities'
                elif re.match(r'^Required\s+(Skills?|Qualifications?)[\s:]*$', line_stripped, re.IGNORECASE):
                    detected_section = 'requirements'
                elif re.match(r'^Preferred\s+(Skills?|Qualifications?)[\s:]*$', line_stripped, re.IGNORECASE):
                    detected_section = 'preferred'

            if detected_section:
                # Save previous section
                if current_section and section_content:
                    sections[current_section] = '\n'.join(section_content)

                # Start new section
                current_section = detected_section
                section_content = []
            elif current_section:
                # Add to current section
                section_content.append(line)
            elif not current_section and line_stripped:
                # Before any section is detected, treat as overview
                if 'overview' not in sections:
                    sections['overview'] = line
                else:
                    sections['overview'] += '\n' + line

        # Save last section
        if current_section and section_content:
            sections[current_section] = '\n'.join(section_content)

        return sections

    def _extract_job_title(self, text: str) -> str:
        """Extract job title from text (usually in first few lines or inferred from content)."""
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        # First, try to find explicit job title in first few lines
        for line in lines[:5]:
            # Skip lines that are clearly not titles
            if line.lower().startswith(('job location', 'location:', 'works in', 'about', 'company')):
                continue

            # Look for common title indicators
            if any(word in line.lower() for word in ['engineer', 'developer', 'manager', 'analyst', 'scientist', 'designer', 'architect', 'lead', 'senior', 'junior', 'specialist', 'consultant']):
                # Make sure it's not too long to be a title
                if len(line) < 100:
                    return line

        # If no explicit title found, try to infer from job content
        text_lower = text.lower()

        # Data Engineering roles
        if 'data engineer' in text_lower or ('data pipeline' in text_lower and 'etl' in text_lower):
            if 'senior' in text_lower or '5' in text_lower or 'lead' in text_lower:
                return "Senior Data Engineer"
            return "Data Engineer"

        # Software Engineering roles
        if 'software engineer' in text_lower:
            if 'senior' in text_lower:
                return "Senior Software Engineer"
            return "Software Engineer"

        # Data Science roles
        if 'data scientist' in text_lower or 'machine learning' in text_lower:
            return "Data Scientist"

        # Analyst roles
        if 'analyst' in text_lower or 'analytics' in text_lower:
            return "Data Analyst"

        # Fallback: return first substantial line
        if lines:
            for line in lines[:3]:
                if len(line) > 5 and len(line) < 100:
                    return line

        return "Unknown Position"

    def _extract_company(self, text: str) -> Optional[str]:
        """Extract company name from text."""
        # Look for patterns like "Company: X" or "at X" or "About us"
        company_pattern = r'(?:company|at|employer)[\s:]+([A-Z][A-Za-z\s&.,]+?)(?:\n|is|was)'
        match = re.search(company_pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        return None

    def _extract_location(self, text: str) -> Optional[str]:
        """Extract location from text."""
        # Look for location patterns
        location_patterns = [
            r'(?:Job\s+)?Location[\s:]+([A-Za-z\s,/]+?)(?:\n|$)',  # Job Location: City, ST / City, ST
            r'Location[\s:]+([A-Za-z\s,/]+?)(?:\n|Works|Job|$)',   # More flexible end
            r'\b(Remote|Hybrid|On-site|Onsite)\b',
            r'([A-Z][a-z]+,\s*[A-Z]{2}(?:\s*/\s*[A-Z][a-z]+,\s*[A-Z]{2})*)',  # City, ST or City, ST / City, ST
            r'([A-Z][a-z]+,\s*[A-Z][a-z]+)'  # City, Country
        ]

        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                location = match.group(1).strip() if match.lastindex else match.group(0).strip()
                # Clean up location string
                location = re.sub(r'\s+', ' ', location)  # Normalize whitespace
                return location

        return None

    def _extract_job_type(self, text: str) -> Optional[str]:
        """Extract job type (Full-time, Part-time, Contract, etc.)."""
        job_types = ['full-time', 'full time', 'part-time', 'part time', 'contract', 'freelance', 'internship', 'temporary']

        text_lower = text.lower()
        for job_type in job_types:
            if job_type in text_lower:
                return job_type.title()

        return None

    def _extract_list_items(self, text: str) -> List[str]:
        """Extract list items (bullets) from text."""
        items = []

        # Split by lines
        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Remove bullet points
            line = re.sub(r'^[•\-*▪◦○●]\s*', '', line)

            # Remove numbering
            line = re.sub(r'^\d+[\.)]\s*', '', line)

            if line and len(line) > 10:  # Ignore very short lines
                items.append(line)

        return items

    def _extract_skills(self, text: str) -> List[str]:
        """Extract technical skills from text."""
        if not text:
            return []

        text_lower = text.lower()
        found_skills = []

        # Look for common skills (with word boundaries to avoid partial matches)
        for skill in self.COMMON_SKILLS:
            # Create a pattern that matches the skill as a whole word or phrase
            pattern = re.compile(r'\b' + re.escape(skill) + r'\b', re.IGNORECASE)
            match = pattern.search(text)
            if match:
                found_skills.append(match.group(0))

        # Look for experience patterns like "X years of Y" or "proficiency in Y"
        skill_patterns = [
            r'(\d+[-\+]?\d*)\s*(?:years?|yrs?)\s+(?:of\s+)?(?:experience\s+)?(?:with\s+|in\s+)?([A-Za-z][A-Za-z0-9\s\.,/+#-]+?)(?=\.|,|;|\n|or\s|and\s|$)',
            r'(?:proficiency|experience|expertise|knowledge|skills?)\s+(?:in|with|of)\s+([A-Za-z][A-Za-z0-9\s\.,/+#-]+?)(?=\.|,|;|\n|and\s|or\s|$)',
            r'(?:strong|advanced|solid|good|working)\s+(?:knowledge|understanding|proficiency|skills?)\s+(?:in|with|of)\s+([A-Za-z][A-Za-z0-9\s\.,/+#-]+?)(?=\.|,|;|\n|and\s|or\s|$)',
            r'(?:familiarity|familiar)\s+with\s+([A-Za-z][A-Za-z0-9\s\.,/+#-]+?)(?=\.|,|;|\n|and\s|or\s|$)'
        ]

        for pattern in skill_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Handle tuples from patterns with capture groups
                if isinstance(match, tuple):
                    skill = match[-1] if match else ''  # Get last capture group
                else:
                    skill = match

                skill = skill.strip()

                # Clean up the skill string
                skill = re.sub(r'\s+', ' ', skill)  # Normalize whitespace
                skill = re.sub(r'[,;.]$', '', skill)  # Remove trailing punctuation

                # Only add if reasonable length and not empty
                if skill and 2 < len(skill) < 60:
                    # Check if it looks like a valid skill (not just common words)
                    if not re.match(r'^(the|and|or|for|with|from|that|this|which)$', skill.lower()):
                        found_skills.append(skill)

        # Look for parenthetical technology lists like "Python (including pandas, numpy)"
        paren_pattern = r'([A-Za-z][A-Za-z0-9\s]+?)\s*\((?:including\s+)?([^)]+)\)'
        paren_matches = re.findall(paren_pattern, text, re.IGNORECASE)
        for tech, subtechs in paren_matches:
            tech = tech.strip()
            if tech and len(tech) < 50:
                found_skills.append(tech)
            # Also extract sub-technologies
            for subtech in re.split(r',|and', subtechs):
                subtech = subtech.strip()
                if subtech and 2 < len(subtech) < 50:
                    found_skills.append(subtech)

        # Remove duplicates while preserving order
        seen = set()
        unique_skills = []
        for skill in found_skills:
            skill_lower = skill.lower().strip()
            # Also normalize common variations
            skill_normalized = re.sub(r'[^a-z0-9\s+#]', '', skill_lower)
            if skill_normalized and skill_normalized not in seen:
                seen.add(skill_normalized)
                unique_skills.append(skill)

        return unique_skills

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from the entire JD."""
        # Combine required and preferred skills as base keywords
        keywords = self._extract_skills(text)

        # Add common action words
        action_words = ['develop', 'design', 'implement', 'manage', 'lead', 'analyze', 'build', 'create', 'maintain', 'optimize', 'collaborate', 'communicate']

        text_lower = text.lower()
        for word in action_words:
            if word in text_lower:
                keywords.append(word)

        # Add important nouns (using simple heuristic)
        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        important_words = [w for w in words if len(w) > 4 and len(w) < 30]

        # Take top frequent words
        from collections import Counter
        word_freq = Counter(important_words)
        top_words = [word for word, count in word_freq.most_common(20) if count > 1]

        keywords.extend(top_words)

        # Remove duplicates
        seen = set()
        unique_keywords = []
        for kw in keywords:
            kw_lower = kw.lower()
            if kw_lower not in seen and len(kw) > 2:
                seen.add(kw_lower)
                unique_keywords.append(kw)

        return unique_keywords[:50]  # Limit to 50 keywords

    def _extract_years_of_experience(self, text: str) -> Optional[str]:
        """Extract years of experience requirement."""
        # Look for patterns like "5+ years", "3-5 years", etc.
        patterns = [
            r'(\d+\+?)\s*(?:years?|yrs?)\s+(?:of\s+)?experience',
            r'(?:minimum|at least)\s+(\d+)\s+(?:years?|yrs?)',
            r'(\d+[-–]\d+)\s+(?:years?|yrs?)'
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1) + " years"

        return None

    def _extract_education_requirement(self, text: str) -> Optional[str]:
        """Extract education requirement."""
        # Look for degree requirements
        degree_pattern = r'(Bachelor\'?s?|Master\'?s?|PhD|Ph\.D\.|B\.S\.|M\.S\.|B\.A\.|M\.A\.)(?:\s+(?:degree|in))?(?:\s+in\s+)?([A-Za-z\s]+)?'
        match = re.search(degree_pattern, text, re.IGNORECASE)

        if match:
            degree = match.group(0)
            # Look for surrounding context
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            context = text[start:end]

            return context.strip()

        return None
