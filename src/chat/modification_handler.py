"""Handler for resume modifications via chat."""

import re
from typing import Dict, Any, Optional, Tuple
from src.models import Resume


class ModificationHandler:
    """Handle resume modifications from natural language requests."""

    @staticmethod
    def detect_modification_intent(user_input: str) -> Optional[str]:
        """
        Detect if user wants to modify something.

        Returns:
            Modification type or None
        """
        user_lower = user_input.lower()

        # Modification patterns
        modification_patterns = {
            'change': ['change', 'update', 'modify', 'edit', 'replace'],
            'add': ['add', 'include', 'insert', 'append'],
            'remove': ['remove', 'delete', 'drop', 'take out'],
            'set': ['set my', 'make my', 'put my']
        }

        for mod_type, keywords in modification_patterns.items():
            if any(keyword in user_lower for keyword in keywords):
                return mod_type

        # Implicit setting patterns (e.g., "my email is...", "my github link is...")
        # These are considered 'set' operations
        implicit_set_fields = ['email', 'phone', 'github', 'linkedin', 'location', 'name','education_institution', 'education_location', 'education_gpa', 'education_degree', 'education_field_of_study', 'education_graduation_date']
        for field in implicit_set_fields:
            if field in user_lower and (' is ' in user_lower or ' link ' in user_lower):
                # Check if it's actually providing a value (not asking a question)
                if not user_lower.startswith('what') and not user_lower.startswith('where'):
                    return 'set'

        return None

    @staticmethod
    def extract_field_and_value(user_input: str) -> Dict[str, Any]:
        """
        Extract field name and new value from user input.

        Examples:
            "Change my email to john@example.com"
            "Update years of experience from 3 to 5"
            "Add skill: Docker"
            "Set my phone to +1 234-567-8900"
        """
        user_lower = user_input.lower()
        result = {'field': None, 'old_value': None, 'new_value': None}

        # Email patterns
        if 'email' in user_lower:
            result['field'] = 'email'
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', user_input)
            if email_match:
                result['new_value'] = email_match.group(0)

        # Phone patterns
        elif 'phone' in user_lower or 'number' in user_lower:
            result['field'] = 'phone'
            phone_match = re.search(r'[\+\d][\d\s\-\(\)]{8,}', user_input)
            if phone_match:
                result['new_value'] = phone_match.group(0).strip()

        # Years of experience
        elif 'year' in user_lower and 'experience' in user_lower:
            result['field'] = 'years_experience'
            # Pattern: "from X to Y" or "to Y"
            from_to_match = re.search(r'from\s+(\d+)\s+to\s+(\d+)', user_lower)
            if from_to_match:
                result['old_value'] = from_to_match.group(1)
                result['new_value'] = from_to_match.group(2)
            else:
                to_match = re.search(r'to\s+(\d+)', user_lower)
                if to_match:
                    result['new_value'] = to_match.group(1)

        # Name
        elif 'name' in user_lower and ('my name' in user_lower or 'change name' in user_lower):
            result['field'] = 'name'
            # Extract name after "to" or "is"
            name_match = re.search(r'(?:to|is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', user_input)
            if name_match:
                result['new_value'] = name_match.group(1)

        # Skills
        elif 'skill' in user_lower:
            result['field'] = 'skill'
            # Pattern: "Add skill: X" or "Add skill X"
            skill_match = re.search(r'(?:skill:?\s+|skill\s+)([A-Za-z][A-Za-z0-9\s\+\#\.\-]+?)(?:\.|,|$|\n)', user_input, re.IGNORECASE)
            if skill_match:
                result['new_value'] = skill_match.group(1).strip()

        # Location
        elif 'location' in user_lower and 'education' in user_lower:
            result['field'] = 'education_location'
            location_match = re.search(r'(?:to|is)\s+([A-Z][a-zA-Z\s,]+)', user_input)
            if location_match:
                result['new_value'] = location_match.group(1).strip()
        elif 'institution' in user_lower and 'education' in user_lower:
            result['field'] = 'education_institution'
            institution_match = re.search(r'(?:to|is)\s+([A-Z][a-zA-Z\s,]+)', user_input)
            if institution_match:
                result['new_value'] = institution_match.group(1).strip()
        elif 'location' in user_lower:
            result['field'] = 'location'
            location_match = re.search(r'(?:to|is)\s+([A-Z][a-zA-Z\s,]+)', user_input)
            if location_match:
                result['new_value'] = location_match.group(1).strip()
        elif 'gpa' in user_lower or 'grade point' in user_lower:
            result['field'] = 'education_gpa'
            # Match decimal numbers like 3.5, 3.85, 4.0
            gpa_match = re.search(r'(?:to|is)\s+(\d+\.\d+)', user_input)
            if gpa_match:
                result['new_value'] = gpa_match.group(1).strip()
        elif ('degree' in user_lower and ('education' in user_lower or 'my degree' in user_lower)) or 'bachelor' in user_lower or 'master' in user_lower:
            result['field'] = 'education_degree'
            degree_match = re.search(r'(?:to|is)\s+([A-Z][a-zA-Z\s,]+)', user_input)
            if degree_match:
                result['new_value'] = degree_match.group(1).strip()
        elif 'field of study' in user_lower:
            result['field'] = 'education_field_of_study'
            field_of_study_match = re.search(r'(?:to|is)\s+([A-Z][a-zA-Z\s,]+)', user_input)
            if field_of_study_match:
                result['new_value'] = field_of_study_match.group(1).strip()
        elif 'graduation date' in user_lower:
            result['field'] = 'education_graduation_date'
            graduation_date_match = re.search(r'(?:to|is)\s+([A-Z][a-z]+,?\s+\d{4})', user_input)
            if graduation_date_match:
                result['new_value'] = graduation_date_match.group(1).strip()
        # LinkedIn
        elif 'linkedin' in user_lower:
            result['field'] = 'linkedin'
            # Try full URL with https
            linkedin_match = re.search(r'https?://(?:www\.)?linkedin\.com/[\w\-/]+', user_input, re.IGNORECASE)
            if linkedin_match:
                result['new_value'] = linkedin_match.group(0)
            else:
                # Try without https
                linkedin_match = re.search(r'linkedin\.com/[\w\-/]+', user_input, re.IGNORECASE)
                if linkedin_match:
                    result['new_value'] = f"https://{linkedin_match.group(0)}"
                else:
                    # Try to extract just the username/path after "is" or "to"
                    # Handle "link is username" specially
                    if 'link is' in user_input.lower():
                        username_match = re.search(r'link\s+is\s+([a-zA-Z0-9\-]+)', user_input, re.IGNORECASE)
                    else:
                        username_match = re.search(r'(?:is|to)\s+([a-zA-Z0-9\-]+)(?:\s|$|\.)', user_input)
                    if username_match:
                        result['new_value'] = f"https://linkedin.com/in/{username_match.group(1)}"

        # GitHub
        elif 'github' in user_lower:
            result['field'] = 'github'
            # Try full URL with https
            github_match = re.search(r'https?://(?:www\.)?github\.com/[\w\-]+', user_input, re.IGNORECASE)
            if github_match:
                result['new_value'] = github_match.group(0)
            else:
                # Try without https
                github_match = re.search(r'github\.com/[\w\-]+', user_input, re.IGNORECASE)
                if github_match:
                    result['new_value'] = f"https://{github_match.group(0)}"
                else:
                    # Try to extract just the username after "is" or "to" or "link"
                    # Handle "link is username" specially
                    if 'link is' in user_input.lower():
                        username_match = re.search(r'link\s+is\s+([a-zA-Z0-9\-]+)', user_input, re.IGNORECASE)
                    else:
                        username_match = re.search(r'(?:is|to)\s+([a-zA-Z0-9\-]+)(?:\s|$|\.)', user_input)
                    if username_match:
                        result['new_value'] = f"https://github.com/{username_match.group(1)}"

        return result

    @staticmethod
    def apply_modification(resume: Resume, field: str, new_value: Any, old_value: Any = None) -> Tuple[bool, str]:
        """
        Apply modification to resume.

        Returns:
            (success, message)
        """
        try:
            if field == 'email':
                resume.contact.email = new_value
                return True, f"✓ Email updated to: {new_value}"

            elif field == 'phone':
                resume.contact.phone = new_value
                return True, f"✓ Phone updated to: {new_value}"

            elif field == 'name':
                resume.contact.full_name = new_value
                return True, f"✓ Name updated to: {new_value}"

            elif field == 'location':
                resume.contact.location = new_value
                return True, f"✓ Location updated to: {new_value}"

            elif field == 'linkedin':
                resume.contact.linkedin = new_value
                return True, f"✓ LinkedIn updated to: {new_value}"

            elif field == 'github':
                resume.contact.github = new_value
                return True, f"✓ GitHub updated to: {new_value}"

            elif field == 'years_experience':
                # Update summary if it exists
                if resume.summary:
                    if old_value:
                        resume.summary = resume.summary.replace(f"{old_value}+", f"{new_value}+")
                        resume.summary = resume.summary.replace(f"{old_value} years", f"{new_value} years")
                    else:
                        # Try to find and replace any year pattern
                        resume.summary = re.sub(r'\d+\+?\s*years?', f"{new_value}+ years", resume.summary, count=1)
                    return True, f"✓ Years of experience updated to: {new_value}+ years"
                else:
                    return False, "No summary found to update"

            elif field == 'skill':
                if new_value not in resume.skills:
                    resume.skills.append(new_value)
                    return True, f"✓ Added skill: {new_value}"
                else:
                    return True, f"ℹ️ Skill '{new_value}' already exists"
            elif field == 'education_location':
                if not resume.education:
                    return False, "No education entries found. Cannot update education location."
                resume.education[-1].location = new_value
                return True, f"✓ Education location updated to: {new_value}"
            elif field == 'education_institution':
                if not resume.education:
                    return False, "No education entries found. Cannot update education institution."
                resume.education[-1].institution = new_value
                return True, f"✓ Education institution updated to: {new_value}"
            elif field == 'education_gpa':
                if not resume.education:
                    return False, "No education entries found. Cannot update GPA."
                resume.education[-1].gpa = new_value
                return True, f"✓ Education GPA updated to: {new_value}"
            elif field == 'education_degree':
                if not resume.education:
                    return False, "No education entries found. Cannot update degree."
                resume.education[-1].degree = new_value
                return True, f"✓ Education degree updated to: {new_value}"
            elif field == 'education_field_of_study':
                if not resume.education:
                    return False, "No education entries found. Cannot update field of study."
                resume.education[-1].field_of_study = new_value
                return True, f"✓ Education field of study updated to: {new_value}"
            elif field == 'education_graduation_date':
                if not resume.education:
                    return False, "No education entries found. Cannot update graduation date."
                resume.education[-1].graduation_date = new_value
                return True, f"✓ Education graduation date updated to: {new_value}"
            else:
                return False, f"Unknown field: {field}"

        except Exception as e:
            return False, f"Error applying modification: {e}"

    @classmethod
    def process_user_request(cls, user_input: str, resume: Resume) -> Tuple[bool, str, Optional[str]]:
        """
        Process user modification request.

        Returns:
            (is_modification, response_message, chat_response)
        """
        # Check if it's a modification request
        mod_intent = cls.detect_modification_intent(user_input)

        if not mod_intent:
            return False, "", None  # Not a modification, use regular chat

        # Extract field and value
        extraction = cls.extract_field_and_value(user_input)

        if not extraction['field'] or not extraction['new_value']:
            return True, "I understand you want to make a change, but I couldn't determine what to modify. Please be more specific. For example:\n- 'Change my email to john@example.com'\n- 'Update years of experience to 5'\n- 'Add skill: Docker'", None

        # Apply modification
        success, message = cls.apply_modification(
            resume,
            extraction['field'],
            extraction['new_value'],
            extraction['old_value']
        )

        if success:
            return True, message, "Your resume has been updated. You can continue to make more changes or proceed to generate the optimized version."
        else:
            return True, f"❌ {message}", None
