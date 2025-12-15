"""Resume generator using LLMs and semantic matching results."""

from typing import List, Dict, Optional
import copy
import re
from src.models import Resume, JobDescription, Experience, Project
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
        max_bullets: int = 25
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
            optimized_text = self.llm_service.generate(prompt, temperature=0.7, max_tokens=2000)

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
        # Ordered from MOST specific to LEAST specific (important!)
        patterns = [
            r'over\s+(\d+\+?)\s+years?\s+of\s+hands-on\s+experience',  # "over 5+ years of hands-on experience" (MOST specific)
            r'(\d+\+?)\s+years?\s+of\s+hands-on\s+experience',  # "5+ years of hands-on experience"
            r'with\s+over\s+(\d+\+?)\s+years',         # "with over 5+ years"
            r'over\s+(\d+\+?)\s+years',                # "over 5 years"
            r'with\s+(\d+\+?)\s+years',                # "with 5+ years"
            r'(\d+\+?)\s+years?\s+of\s+experience',    # "5+ years of experience"
            r'(\d+\+?)\s+years?\s+in',                 # "5 years in"
            r'(\d+\+?)\s+years?\s+\w+',                # "5+ years [any word]" (more flexible)
            r'(\d+\+?)\s+years?',                      # "5+ years" (catch-all, LEAST specific)
        ]

        for i, pattern in enumerate(patterns, 1):
            match = re.search(pattern, summary, re.IGNORECASE)
            if match:
                years = match.group(1)
                matched_text = match.group(0)
                match_position = match.start()
                context = summary[max(0, match_position-20):min(len(summary), match_position+len(matched_text)+20)]
                
                if '+' not in years:
                    years += '+'
                return years

        return ""

    def optimize_summary(
        self,
        original_summary: str,
        jd: JobDescription,
        key_skills: List[str],
        genai_skills: List[str] = None
    ) -> str:
        """
        Optimize professional summary for a job description.

        Args:
            original_summary: Original summary text
            jd: Job description
            key_skills: Top skills to highlight
            genai_skills: GenAI/ML skills if applicable

        Returns:
            Optimized summary text
        """
        print("\n  Optimizing professional summary...")

        # Extract years from original summary
        years_experience = self._extract_years_from_summary(original_summary)
        if not years_experience and jd.years_of_experience:
            print(f"    ⚠️  No years of experience found in summary, using JD years of experience: {jd.years_of_experience}")
            years_experience = jd.years_of_experience
        else:
            print(f"    ✓ Found years of experience in summary: {years_experience} from JD: {jd.years_of_experience}")

        # Check if GenAI skills should be mentioned
        if genai_skills and len(genai_skills) > 0:
            print(f"    ✓ Including GenAI/ML skills in summary: {len(genai_skills)} skills")

        prompt = self.prompt_templates.get_summary_optimization_prompt(
            original_summary=original_summary,
            jd_overview=jd.overview or jd.responsibilities[0] if jd.responsibilities else "",
            job_title=jd.job_title,
            key_skills=key_skills,
            years_experience=years_experience,
            genai_skills=genai_skills
        )

        try:
            # Increased max_tokens for longer summaries (5-7 sentences)
            optimized_summary = self.llm_service.generate(prompt, temperature=0.7, max_tokens=400)
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
            enhanced = self.llm_service.generate(prompt, temperature=0.7, max_tokens=150)
            # Clean up any remaining bullet symbols and bold markers if needed
            enhanced = enhanced.strip().lstrip('•▪-*➤').strip()
            return enhanced

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
            optimized_text = self.llm_service.generate(prompt, temperature=0.5, max_tokens=800)

            # Parse skills from response
            skills = self._parse_skills_from_response(optimized_text)

            print(f"    ✓ Optimized skills section ({len(skills)} skills)")
            return skills

        except Exception as e:
            print(f"    ⚠️  Error optimizing skills: {e}")
            return current_skills

    def optimize_project(
        self,
        project: Project,
        jd: JobDescription,
        max_bullets: int = 8
    ) -> Project:
        """
        Optimize a project section for job description.

        Args:
            project: Project to optimize
            jd: Job description
            max_bullets: Maximum bullets to generate (default 8)

        Returns:
            Optimized Project object
        """
        print(f"\n  Optimizing project: {project.name}...")

        # Extract JD requirements and technologies
        jd_requirements = jd.responsibilities[:5] if jd.responsibilities else []
        jd_technologies = jd.required_skills + jd.preferred_skills

        # Generate optimization prompt
        prompt = self.prompt_templates.get_project_optimization_prompt(
            project_name=project.name,
            project_description=project.description or "",
            project_bullets=project.bullets,
            project_technologies=project.technologies,
            jd_requirements=jd_requirements,
            jd_technologies=jd_technologies
        )

        # Generate optimized bullets
        try:
            optimized_text = self.llm_service.generate(prompt, temperature=0.7, max_tokens=1500)

            # Parse bullets from response
            optimized_bullets = self._parse_bullets_from_response(optimized_text)

            # Limit to max_bullets
            if len(optimized_bullets) > max_bullets:
                optimized_bullets = optimized_bullets[:max_bullets]

            # Create optimized project
            optimized_project = Project(
                name=project.name,
                description=project.description,
                technologies=project.technologies,
                bullets=optimized_bullets,
                url=project.url,
                date=project.date
            )

            print(f"    ✓ Generated {len(optimized_bullets)} optimized bullets")
            return optimized_project

        except Exception as e:
            print(f"    ⚠️  Error optimizing project: {e}")
            return project  # Return original on error

    def generate_optimized_resume(
        self,
        resume: Resume,
        jd: JobDescription,
        match_results: Optional[Dict] = None,
        optimize_summary: bool = True,
        optimize_skills: bool = True,
        optimize_all_experiences: bool = True,
        optimize_projects: bool = True
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
            optimize_projects: Whether to optimize projects

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
                key_skills=top_skills,
                genai_skills=resume.genai_skills if resume.genai_skills else None
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

        # Optimize projects
        if optimize_projects and resume.projects:
            optimized_projects = []
            num_projects_to_optimize = min(3, len(resume.projects))  # Optimize top 3 projects

            for project in resume.projects[:num_projects_to_optimize]:
                optimized_proj = self.optimize_project(
                    project=project,
                    jd=jd
                )
                optimized_projects.append(optimized_proj)

            # Keep remaining projects as-is
            optimized_projects.extend(resume.projects[num_projects_to_optimize:])
            optimized_resume.projects = optimized_projects

        print("\n" + "=" * 60)
        print("✓ RESUME OPTIMIZATION COMPLETE")
        print("=" * 60)

        return optimized_resume

    def _parse_bullets_from_response(self, response: str) -> List[str]:
        """Parse bullet points from LLM response (ATS-friendly format)."""
        bullets = []

        # Split by lines
        lines = response.strip().split('\n')

        for line in lines:
            line = line.strip()

            # Skip empty lines and headers
            if not line or line.lower().startswith(('optimized', 'rewritten', 'bullets:', 'bullet', 'output', 'format:')):
                continue

            # Remove any bullet symbols and numbering that might still be present
            line = line.lstrip('•▪-*➤123456789.').strip()

            # Skip lines that are too short (likely headers or artifacts)
            if line and len(line) > 15:  # Must be substantial
                bullets.append(line)

        return bullets

    def _parse_skills_from_response(self, response: str) -> List[str]:
        """
        Parse skills list from LLM response (ATS-friendly format with categories).

        Returns list of categorized skill lines for table formatting in DOCX.
        Format: ["**Category**: skill1, skill2, skill3", ...]
        """
        skills = []

        # Remove any headers
        response = response.replace('OPTIMIZED SKILLS:', '').replace('Skills:', '').replace('TECHNICAL SKILLS TABLE:', '').strip()

        # Split by lines
        lines = response.split('\n')

        current_category = None
        current_skills = []

        for line in lines:
            line = line.strip()

            if not line:
                # Empty line - save current category if any
                if current_category and current_skills:
                    skills.append(f"**{current_category}**: {', '.join(current_skills)}")
                    current_category = None
                    current_skills = []
                continue

            # Check if this is a category header line with format: **Category**: skills OR **Category** (on its own line)
            if line.startswith('**') and ('**:' in line or line.endswith('**')):
                # Save previous category if any
                if current_category and current_skills:
                    skills.append(f"**{current_category}**: {', '.join(current_skills)}")
                    current_skills = []

                # Parse new category
                if '**:' in line or '**: ' in line:
                    # Format: **Category**: skill1, skill2
                    # Keep the line as-is (already has proper format)
                    skills.append(line)
                    current_category = None
                else:
                    # Format: **Category** (skills on next line)
                    current_category = line.replace('**', '').strip()
            elif current_category:
                # Skills for current category (on separate line after category header)
                category_skills = [s.strip() for s in line.split(',') if s.strip()]
                current_skills.extend(category_skills)
            elif ':' in line and not line.startswith('**'):
                # Format without **: "Category: skill1, skill2"
                # Add ** markers
                parts = line.split(':', 1)
                if len(parts) == 2:
                    category = parts[0].strip()
                    skills_part = parts[1].strip()
                    skills.append(f"**{category}**: {skills_part}")

        # Don't forget last category
        if current_category and current_skills:
            skills.append(f"**{current_category}**: {', '.join(current_skills)}")

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
