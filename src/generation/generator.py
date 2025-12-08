"""Resume generator using LLMs and semantic matching results."""

from typing import List, Dict, Optional
import copy
import re
from src.models import Resume, JobDescription, Experience
from src.generation.llm_service import LLMService, get_default_llm_service
from src.generation.prompts import PromptTemplates
from src.analysis.skill_matcher import SkillMatcher


class ResumeGenerator:
    """Generate optimized resume content using LLMs."""

    def __init__(self, llm_service: Optional[LLMService] = None):
        """
        Initialize resume generator.

        Args:
            llm_service: LLM service instance (creates default if None)
        """
        self.llm_service = llm_service or get_default_llm_service()
        self.prompt_templates = PromptTemplates()
        self.skill_matcher = SkillMatcher()

    def optimize_experience_bullets(
        self,
        experience: Experience,
        jd: JobDescription,
        match_results: Optional[Dict] = None,
        max_bullets: int = 7
    ) -> Experience:
        """
        Optimize experience bullets for a specific job description.

        Args:
            experience: Experience object to optimize
            jd: Job description to optimize for
            match_results: Semantic matching results (optional)
            max_bullets: Maximum number of bullets to generate

        Returns:
            Optimized Experience object
        """
        print(f"\n  Optimizing: {experience.title} at {experience.company}")

        # Get missing keywords
        all_skills_text = " ".join(experience.bullets)
        resume_skills = self.skill_matcher.extract_skills_from_text(
            all_skills_text,
            jd.required_skills + jd.preferred_skills
        )

        missing_keywords = []
        for skill in jd.required_skills[:10]:
            if skill not in resume_skills:
                missing_keywords.append(skill)

        # Generate prompt for multi-bullet optimization
        prompt = self.prompt_templates.get_multi_bullet_optimization_prompt(
            original_bullets=experience.bullets,
            jd_responsibilities=jd.responsibilities,
            missing_keywords=missing_keywords,
            company=experience.company,
            title=experience.title
        )

        # Generate optimized bullets
        try:
            optimized_text = self.llm_service.generate(prompt, temperature=0.7, max_tokens=800)

            # Parse the generated bullets
            optimized_bullets = self._parse_bullets_from_response(optimized_text)

            # Create optimized experience
            optimized_exp = copy.deepcopy(experience)
            optimized_exp.bullets = optimized_bullets[:max_bullets]

            print(f"    ✓ Generated {len(optimized_exp.bullets)} optimized bullets")
            return optimized_exp

        except Exception as e:
            print(f"    ⚠️  Error optimizing bullets: {e}")
            return experience  # Return original on error

    def _extract_years_from_summary(self, summary: str) -> str:
        """Extract years of experience from summary text."""
        # Pattern: "3+ years", "5 years", "over 3 years", etc.
        patterns = [
            r'(\d+\+?)\s+years?\s+of\s+experience',
            r'over\s+(\d+)\s+years',
            r'(\d+)\s+years?\s+in',
            r'with\s+(\d+\+?)\s+years',
        ]

        for pattern in patterns:
            match = re.search(pattern, summary, re.IGNORECASE)
            if match:
                years = match.group(1)
                if '+' not in years:
                    years += '+'
                return years

        return ""

    def optimize_summary(
        self,
        original_summary: str,
        jd: JobDescription,
        key_skills: List[str]
    ) -> str:
        """
        Optimize professional summary for a job description.

        Args:
            original_summary: Original summary text
            jd: Job description
            key_skills: Top skills to highlight

        Returns:
            Optimized summary text
        """
        print("\n  Optimizing professional summary...")

        # Extract years from original summary
        years_experience = self._extract_years_from_summary(original_summary)
        if not years_experience and jd.years_of_experience:
            years_experience = jd.years_of_experience

        prompt = self.prompt_templates.get_summary_optimization_prompt(
            original_summary=original_summary,
            jd_overview=jd.overview or jd.responsibilities[0] if jd.responsibilities else "",
            job_title=jd.job_title,
            key_skills=key_skills,
            years_experience=years_experience
        )

        try:
            optimized_summary = self.llm_service.generate(prompt, temperature=0.7, max_tokens=300)
            print(f"    ✓ Generated optimized summary")
            return optimized_summary.strip()

        except Exception as e:
            print(f"    ⚠️  Error optimizing summary: {e}")
            return original_summary

    def enhance_single_bullet(
        self,
        bullet: str,
        jd_requirement: Optional[str] = None,
        missing_keywords: List[str] = None
    ) -> str:
        """
        Enhance a single bullet point.

        Args:
            bullet: Original bullet text
            jd_requirement: Related JD requirement (optional)
            missing_keywords: Keywords to inject (optional)

        Returns:
            Enhanced bullet text
        """
        if jd_requirement and missing_keywords:
            prompt = self.prompt_templates.get_bullet_rewrite_prompt(
                original_bullet=bullet,
                jd_requirement=jd_requirement,
                missing_keywords=missing_keywords
            )
        else:
            prompt = self.prompt_templates.get_achievement_enhancement_prompt(
                bullet=bullet,
                add_metrics=True
            )

        try:
            enhanced = self.llm_service.generate(prompt, temperature=0.7, max_tokens=200)
            return enhanced.strip().lstrip('•').strip()

        except Exception as e:
            print(f"    ⚠️  Error enhancing bullet: {e}")
            return bullet

    def optimize_skills_section(
        self,
        current_skills: List[str],
        jd: JobDescription
    ) -> List[str]:
        """
        Optimize skills section for a job description.

        Args:
            current_skills: Current skills list
            jd: Job description

        Returns:
            Optimized skills list
        """
        print("\n  Optimizing skills section...")

        prompt = self.prompt_templates.get_skills_optimization_prompt(
            current_skills=current_skills,
            jd_required_skills=jd.required_skills,
            jd_preferred_skills=jd.preferred_skills
        )

        try:
            optimized_text = self.llm_service.generate(prompt, temperature=0.5, max_tokens=400)

            # Parse skills from response
            skills = self._parse_skills_from_response(optimized_text)

            print(f"    ✓ Optimized skills section ({len(skills)} skills)")
            return skills

        except Exception as e:
            print(f"    ⚠️  Error optimizing skills: {e}")
            return current_skills

    def generate_optimized_resume(
        self,
        resume: Resume,
        jd: JobDescription,
        match_results: Optional[Dict] = None,
        optimize_summary: bool = True,
        optimize_skills: bool = True,
        optimize_all_experiences: bool = True
    ) -> Resume:
        """
        Generate fully optimized resume for a job description.

        Args:
            resume: Original resume
            jd: Job description to optimize for
            match_results: Semantic matching results (optional)
            optimize_summary: Whether to optimize summary
            optimize_skills: Whether to optimize skills
            optimize_all_experiences: Whether to optimize all experiences

        Returns:
            Optimized Resume object
        """
        print("\n" + "=" * 60)
        print("GENERATING OPTIMIZED RESUME")
        print("=" * 60)

        # Create a deep copy
        optimized_resume = copy.deepcopy(resume)

        # Optimize summary
        if optimize_summary and resume.summary:
            # Get top skills from matching
            matched_skills = self.skill_matcher.match_skills(
                required_skills=jd.required_skills,
                resume_skills=resume.skills,
                experience_text=""
            )

            top_skills = [m['required'] for m in matched_skills['matched_skills'][:8]]

            optimized_resume.summary = self.optimize_summary(
                original_summary=resume.summary,
                jd=jd,
                key_skills=top_skills
            )

        # Optimize experiences
        if optimize_all_experiences:
            optimized_experiences = []
            for exp in resume.experience[:3]:  # Optimize top 3 experiences
                optimized_exp = self.optimize_experience_bullets(
                    experience=exp,
                    jd=jd,
                    match_results=match_results
                )
                optimized_experiences.append(optimized_exp)

            # Keep remaining experiences as-is
            optimized_experiences.extend(resume.experience[3:])
            optimized_resume.experience = optimized_experiences

        # Optimize skills
        if optimize_skills:
            optimized_resume.skills = self.optimize_skills_section(
                current_skills=resume.skills,
                jd=jd
            )

        print("\n" + "=" * 60)
        print("✓ RESUME OPTIMIZATION COMPLETE")
        print("=" * 60)

        return optimized_resume

    def _parse_bullets_from_response(self, response: str) -> List[str]:
        """Parse bullet points from LLM response."""
        bullets = []

        # Split by lines
        lines = response.strip().split('\n')

        for line in lines:
            line = line.strip()

            # Skip empty lines and headers
            if not line or line.lower().startswith(('optimized', 'rewritten', 'bullets:', 'bullet')):
                continue

            # Remove bullet symbols and numbering
            line = line.lstrip('•▪-*123456789.').strip()

            if line and len(line) > 20:  # Must be substantial
                bullets.append(line)

        return bullets

    def _parse_skills_from_response(self, response: str) -> List[str]:
        """Parse skills list from LLM response."""
        skills = []

        # Remove any headers
        response = response.replace('OPTIMIZED SKILLS:', '').replace('Skills:', '').strip()

        # Split by lines
        lines = response.split('\n')

        for line in lines:
            line = line.strip()

            if not line:
                continue

            # Check if it's a categorized line (Category: skills)
            if ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    skills_part = parts[1]
                else:
                    skills_part = line
            else:
                skills_part = line

            # Split by commas
            line_skills = [s.strip() for s in skills_part.split(',') if s.strip()]
            skills.extend(line_skills)

        return skills

    def generate_comparison_report(
        self,
        original_resume: Resume,
        optimized_resume: Resume,
        jd: JobDescription
    ) -> Dict:
        """
        Generate a comparison report between original and optimized resumes.

        Args:
            original_resume: Original resume
            optimized_resume: Optimized resume
            jd: Job description

        Returns:
            Comparison report dictionary
        """
        report = {
            'summary_changed': original_resume.summary != optimized_resume.summary,
            'skills_added': [],
            'skills_removed': [],
            'experience_changes': []
        }

        # Skills comparison
        orig_skills = set(original_resume.skills)
        opt_skills = set(optimized_resume.skills)

        report['skills_added'] = list(opt_skills - orig_skills)
        report['skills_removed'] = list(orig_skills - opt_skills)

        # Experience comparison
        for i, (orig_exp, opt_exp) in enumerate(zip(original_resume.experience, optimized_resume.experience)):
            if orig_exp.bullets != opt_exp.bullets:
                report['experience_changes'].append({
                    'index': i,
                    'company': orig_exp.company,
                    'original_bullets': len(orig_exp.bullets),
                    'optimized_bullets': len(opt_exp.bullets)
                })

        return report

    def generate_enhanced_professional_summary(
        self,
        resume: Resume,
        jd: JobDescription,
        years_of_experience: str = "5+"
    ) -> str:
        """
        Generate enhanced professional summary with WHR format (20-25 bullets).
        Uses sample_prompts.md specifications.

        Args:
            resume: Resume object
            jd: Job description
            years_of_experience: Years of experience string

        Returns:
            Enhanced professional summary text
        """
        print("\n  Generating enhanced professional summary (20-25 bullets)...")

        # Compile experience text
        experience_parts = []
        for exp in resume.experience:
            experience_parts.append(f"{exp.title} at {exp.company} ({exp.start_date} - {exp.end_date})")
            experience_parts.extend(exp.bullets[:5])  # Top 5 bullets per experience

        experience_text = "\n".join(experience_parts)

        # Get full JD text
        jd_text = f"Job Title: {jd.job_title}\n"
        jd_text += f"Responsibilities:\n" + "\n".join(jd.responsibilities)
        jd_text += f"\nRequired Skills: " + ", ".join(jd.required_skills)

        # Generate prompt
        prompt = self.prompt_templates.get_enhanced_professional_summary_prompt(
            experience_text=experience_text,
            job_description=jd_text,
            years_of_experience=years_of_experience,
            job_title=jd.job_title or "Data Engineer"
        )

        try:
            summary = self.llm_service.generate(prompt, temperature=0.7, max_tokens=1500)
            print(f"    ✓ Generated enhanced summary")
            return summary.strip()
        except Exception as e:
            print(f"    ⚠️  Error generating enhanced summary: {e}")
            return resume.summary or ""

    def generate_technical_skills_table(
        self,
        resume: Resume,
        jd: JobDescription
    ) -> str:
        """
        Generate technical skills organized in a table by category.
        Uses sample_prompts.md specifications.

        Args:
            resume: Resume object
            jd: Job description

        Returns:
            Technical skills table text
        """
        print("\n  Generating technical skills table...")

        # Get full JD text
        jd_text = f"Job Title: {jd.job_title}\n"
        jd_text += f"Required Skills: " + ", ".join(jd.required_skills)
        jd_text += f"\nPreferred Skills: " + ", ".join(jd.preferred_skills)

        # Generate prompt
        prompt = self.prompt_templates.get_technical_skills_table_prompt(
            current_skills=resume.skills,
            jd_text=jd_text
        )

        try:
            skills_table = self.llm_service.generate(prompt, temperature=0.5, max_tokens=800)
            print(f"    ✓ Generated technical skills table")
            return skills_table.strip()
        except Exception as e:
            print(f"    ⚠️  Error generating skills table: {e}")
            return ""

    def generate_client_environment_section(
        self,
        experience: Experience,
        jd: JobDescription,
        is_fresher_role: bool = False
    ) -> Dict[str, any]:
        """
        Generate client/environment section with detailed bullets.
        Uses sample_prompts.md specifications.

        Args:
            experience: Experience object
            jd: Job description
            is_fresher_role: Whether this is an entry-level role

        Returns:
            Dict with 'environment' and 'bullets' keys
        """
        print(f"\n  Generating client/environment section for {experience.company}...")

        # Get full JD text
        jd_text = f"Job Title: {jd.job_title}\n"
        jd_text += f"Responsibilities:\n" + "\n".join(jd.responsibilities)
        jd_text += f"\nRequired Skills: " + ", ".join(jd.required_skills)

        # Generate prompt
        prompt = self.prompt_templates.get_client_environment_prompt(
            company=experience.company,
            location=experience.location or "N/A",
            start_date=experience.start_date or "N/A",
            end_date=experience.end_date or "Present",
            is_current=experience.is_current,
            original_bullets=experience.bullets,
            job_description=jd_text,
            is_fresher_role=is_fresher_role
        )

        try:
            response = self.llm_service.generate(prompt, temperature=0.7, max_tokens=1500)

            # Parse environment and bullets
            parts = response.split("CLIENT EXPERIENCE BULLETS:")
            if len(parts) == 2:
                environment = parts[0].replace("ENVIRONMENT:", "").strip()
                bullets_text = parts[1].strip()
            else:
                # Try alternate parsing
                lines = response.split("\n")
                environment_lines = []
                bullet_lines = []
                in_environment = True

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith("Environment:"):
                        in_environment = True
                        environment_lines.append(line.replace("Environment:", "").strip())
                    elif in_environment and (":" in line or "," in line):
                        environment_lines.append(line)
                    else:
                        in_environment = False
                        if line and len(line) > 20:
                            bullet_lines.append(line)

                environment = " ".join(environment_lines)
                bullets_text = "\n".join(bullet_lines)

            # Parse bullets
            bullets = []
            for line in bullets_text.split("\n"):
                line = line.strip().lstrip("•▪-*123456789.").strip()
                if line and len(line) > 20:
                    bullets.append(line)

            print(f"    ✓ Generated environment section and {len(bullets)} bullets")

            return {
                'environment': environment,
                'bullets': bullets
            }

        except Exception as e:
            print(f"    ⚠️  Error generating client/environment section: {e}")
            return {
                'environment': "",
                'bullets': experience.bullets
            }

    def calculate_ats_score(
        self,
        resume: Resume,
        jd: JobDescription
    ) -> Dict[str, any]:
        """
        Calculate ATS score for resume vs job description.
        Uses sample_prompts.md specifications.

        Args:
            resume: Resume object
            jd: Job description

        Returns:
            Dict with score breakdown and recommendations
        """
        print("\n  Calculating ATS score...")

        # Build resume text
        resume_text = f"Name: {resume.contact.full_name}\n\n"
        if resume.summary:
            resume_text += f"Summary: {resume.summary}\n\n"

        resume_text += "Experience:\n"
        for exp in resume.experience:
            resume_text += f"{exp.title} at {exp.company} ({exp.start_date} - {exp.end_date})\n"
            for bullet in exp.bullets:
                resume_text += f"• {bullet}\n"
            resume_text += "\n"

        resume_text += f"Skills: {', '.join(resume.skills)}\n"

        # Build JD text
        jd_text = f"Job Title: {jd.job_title}\n"
        jd_text += f"Responsibilities:\n" + "\n".join([f"• {r}" for r in jd.responsibilities])
        jd_text += f"\n\nRequired Skills: " + ", ".join(jd.required_skills)

        # Generate prompt
        prompt = self.prompt_templates.get_ats_score_prompt(
            resume_text=resume_text,
            job_description=jd_text
        )

        try:
            ats_analysis = self.llm_service.generate(prompt, temperature=0.3, max_tokens=1000)
            print(f"    ✓ Generated ATS analysis")

            return {
                'analysis_text': ats_analysis,
                'raw_resume': resume_text,
                'raw_jd': jd_text
            }

        except Exception as e:
            print(f"    ⚠️  Error calculating ATS score: {e}")
            return {
                'analysis_text': f"Error: {e}",
                'raw_resume': resume_text,
                'raw_jd': jd_text
            }

    def generate_job_application_email(
        self,
        resume: Resume,
        jd: JobDescription,
        key_qualifications: List[str] = None
    ) -> str:
        """
        Generate email subject and body for job application.
        Uses sample_prompts.md specifications.

        Args:
            resume: Resume object
            jd: Job description
            key_qualifications: Top qualifications to highlight

        Returns:
            Email text with subject and body
        """
        print("\n  Generating job application email...")

        # Auto-detect key qualifications if not provided
        if not key_qualifications:
            # Match resume skills to JD required skills
            matched_skills = [skill for skill in resume.skills if any(
                req.lower() in skill.lower() for req in jd.required_skills
            )]
            key_qualifications = matched_skills[:5]

        # Generate prompt
        prompt = self.prompt_templates.get_email_application_prompt(
            job_title=jd.job_title,
            company=jd.company or "the company",
            job_description=f"Responsibilities: {', '.join(jd.responsibilities[:3])}...",
            candidate_name=resume.contact.full_name,
            key_qualifications=key_qualifications
        )

        try:
            email_text = self.llm_service.generate(prompt, temperature=0.7, max_tokens=500)
            print(f"    ✓ Generated job application email")
            return email_text.strip()
        except Exception as e:
            print(f"    ⚠️  Error generating email: {e}")
            return ""
