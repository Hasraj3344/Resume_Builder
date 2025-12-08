"""Intelligent skill matching with abbreviations, variations, and semantic matching."""

import re
from typing import List, Dict, Set, Tuple
from collections import defaultdict


class SkillMatcher:
    """Intelligent skill matcher that handles variations, abbreviations, and context."""

    # Common skill abbreviations and their full forms
    SKILL_ABBREVIATIONS = {
        'adf': ['azure data factory', 'azure datafactory'],
        'aws': ['amazon web services'],
        'gcp': ['google cloud platform', 'google cloud'],
        'ci/cd': ['cicd', 'continuous integration', 'continuous deployment', 'ci cd'],
        'ml': ['machine learning'],
        'ai': ['artificial intelligence'],
        'nlp': ['natural language processing'],
        'etl': ['extract transform load', 'extract-transform-load'],
        'elt': ['extract load transform'],
        'api': ['application programming interface'],
        'rest': ['restful', 'rest api', 'restful api'],
        'sql': ['structured query language'],
        'nosql': ['no sql', 'non-sql'],
        'db': ['database'],
        'k8s': ['kubernetes'],
        'pyspark': ['py spark', 'apache pyspark'],
        'bi': ['business intelligence'],
        'iot': ['internet of things'],
        'devops': ['dev ops'],
        'saas': ['software as a service'],
        'paas': ['platform as a service'],
        'iaas': ['infrastructure as a service'],
    }

    # Skill synonyms and variations
    SKILL_SYNONYMS = {
        'python': ['python3', 'py'],
        'javascript': ['js', 'ecmascript'],
        'typescript': ['ts'],
        'docker': ['containerization', 'containers'],
        'kubernetes': ['k8s', 'container orchestration'],
        'databricks': ['databricks platform', 'databricks workspace'],
        'spark': ['apache spark', 'pyspark'],
        'kafka': ['apache kafka'],
        'airflow': ['apache airflow'],
        'postgresql': ['postgres', 'psql'],
        'mongodb': ['mongo'],
        'github': ['github actions', 'gh'],
        'gitlab': ['gitlab ci'],
        'azure': ['microsoft azure', 'azure cloud'],
        'aws': ['amazon aws', 'amazon web services'],
        'data engineering': ['data engineer', 'data pipeline', 'data pipelines'],
        'data science': ['data scientist'],
        'machine learning': ['ml', 'machine learning engineer'],
        'data modeling': ['data model', 'dimensional modeling'],
        'data governance': ['data quality', 'governance framework'],
        'unity catalog': ['unity', 'databricks unity catalog'],
        'delta lake': ['delta', 'databricks delta'],
        'data warehouse': ['dwh', 'data warehousing'],
        'data lake': ['datalake'],
        'power bi': ['powerbi', 'microsoft power bi'],
        'tableau': ['tableau desktop', 'tableau server'],
    }

    # Reverse mapping: full form -> abbreviation
    ABBREVIATION_MAP = {}
    for abbr, full_forms in SKILL_ABBREVIATIONS.items():
        for full_form in full_forms:
            ABBREVIATION_MAP[full_form] = abbr

    def __init__(self):
        """Initialize the skill matcher."""
        pass

    def normalize_skill(self, skill: str) -> str:
        """Normalize a skill string for comparison."""
        # Convert to lowercase
        skill = skill.lower().strip()

        # Remove special characters except common ones
        skill = re.sub(r'[^\w\s\-+#/.]', ' ', skill)

        # Normalize whitespace
        skill = ' '.join(skill.split())

        return skill

    def get_skill_variations(self, skill: str) -> Set[str]:
        """Get all variations of a skill (abbreviations, synonyms, etc.)."""
        normalized = self.normalize_skill(skill)
        variations = {normalized}

        # Add abbreviation
        if normalized in self.ABBREVIATION_MAP:
            variations.add(self.ABBREVIATION_MAP[normalized])

        # Add full forms if this is an abbreviation
        if normalized in self.SKILL_ABBREVIATIONS:
            variations.update(self.SKILL_ABBREVIATIONS[normalized])

        # Add synonyms
        if normalized in self.SKILL_SYNONYMS:
            variations.update(self.SKILL_SYNONYMS[normalized])

        # Check if this skill is a synonym of another
        for main_skill, synonyms in self.SKILL_SYNONYMS.items():
            if normalized in synonyms:
                variations.add(main_skill)
                variations.update(synonyms)

        return variations

    def extract_skills_from_text(self, text: str, known_skills: List[str]) -> Set[str]:
        """Extract skills mentioned in text (like experience bullets)."""
        if not text:
            return set()

        text_lower = text.lower()
        found_skills = set()

        # Check each known skill and its variations
        for skill in known_skills:
            skill_variations = self.get_skill_variations(skill)

            for variation in skill_variations:
                # Use word boundaries for exact matches
                pattern = r'\b' + re.escape(variation) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills.add(skill)
                    break

        return found_skills

    def match_skill(self, skill1: str, skill2: str) -> bool:
        """Check if two skills match (considering variations)."""
        # Get all variations of both skills
        variations1 = self.get_skill_variations(skill1)
        variations2 = self.get_skill_variations(skill2)

        # Check for any overlap
        if variations1.intersection(variations2):
            return True

        # Check for substring matches (one is contained in the other)
        norm1 = self.normalize_skill(skill1)
        norm2 = self.normalize_skill(skill2)

        if len(norm1) > 3 and len(norm2) > 3:
            if norm1 in norm2 or norm2 in norm1:
                return True

        return False

    def match_skills(
        self,
        required_skills: List[str],
        resume_skills: List[str],
        experience_text: str = ""
    ) -> Dict:
        """
        Match required skills against resume skills and experience.

        Args:
            required_skills: List of skills required by the job
            resume_skills: List of skills from resume skills section
            experience_text: Combined text from all experience bullets

        Returns:
            Dictionary with match results
        """
        # Extract skills mentioned in experience
        experience_skills = self.extract_skills_from_text(
            experience_text,
            required_skills
        )

        # Combine resume skills and experience skills
        all_resume_skills = set([self.normalize_skill(s) for s in resume_skills])

        matched_skills = []
        missing_skills = []
        match_details = []

        for req_skill in required_skills:
            req_normalized = self.normalize_skill(req_skill)
            matched = False
            match_source = None
            matched_as = None

            # Check direct match in resume skills
            for resume_skill in resume_skills:
                if self.match_skill(req_skill, resume_skill):
                    matched = True
                    match_source = 'skills_section'
                    matched_as = resume_skill
                    break

            # If not found in skills section, check experience
            if not matched and req_skill in experience_skills:
                matched = True
                match_source = 'experience'
                matched_as = req_skill

            if matched:
                matched_skills.append({
                    'required': req_skill,
                    'matched_as': matched_as,
                    'source': match_source
                })
            else:
                missing_skills.append(req_skill)

        # Calculate match percentage
        match_percentage = len(matched_skills) / len(required_skills) if required_skills else 0

        return {
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'match_percentage': match_percentage,
            'total_required': len(required_skills),
            'total_matched': len(matched_skills),
            'skills_from_section': sum(1 for m in matched_skills if m['source'] == 'skills_section'),
            'skills_from_experience': sum(1 for m in matched_skills if m['source'] == 'experience')
        }

    def get_skill_suggestions(self, missing_skills: List[str], resume_skills: List[str]) -> List[Dict]:
        """Suggest skills that are close matches or related to missing skills."""
        suggestions = []

        for missing in missing_skills:
            missing_variations = self.get_skill_variations(missing)

            # Check if any resume skill is a close match
            close_matches = []
            for resume_skill in resume_skills:
                resume_normalized = self.normalize_skill(resume_skill)

                # Check if resume skill contains the missing skill or vice versa
                for variation in missing_variations:
                    if variation in resume_normalized or resume_normalized in variation:
                        close_matches.append(resume_skill)
                        break

            if close_matches:
                suggestions.append({
                    'missing_skill': missing,
                    'close_matches': close_matches,
                    'suggestion': f"You have '{close_matches[0]}' - consider also mentioning '{missing}'"
                })

        return suggestions
