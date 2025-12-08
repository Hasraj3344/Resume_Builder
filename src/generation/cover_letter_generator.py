"""Cover letter generator using LLMs and RAG."""

from typing import List, Dict, Optional
from src.models import Resume, JobDescription
from src.generation.llm_service import LLMService, get_default_llm_service
from src.generation.cover_letter_prompts import CoverLetterPrompts, CoverLetterStyle
from src.rag.retriever import RAGRetriever
from src.analysis.skill_matcher import SkillMatcher


class CoverLetterGenerator:
    """Generate tailored cover letters using resume-JD matching."""

    def __init__(
        self,
        llm_service: Optional[LLMService] = None,
        rag_retriever: Optional[RAGRetriever] = None
    ):
        """
        Initialize cover letter generator.

        Args:
            llm_service: LLM service instance
            rag_retriever: RAG retriever for semantic matching
        """
        self.llm_service = llm_service or get_default_llm_service()
        self.rag_retriever = rag_retriever or RAGRetriever()
        self.prompts = CoverLetterPrompts()
        self.skill_matcher = SkillMatcher()

    def generate_cover_letter(
        self,
        resume: Resume,
        jd: JobDescription,
        style: CoverLetterStyle = CoverLetterStyle.PROFESSIONAL,
        why_interested: str = None,
        company_research: str = None
    ) -> Dict[str, any]:
        """
        Generate a complete cover letter.

        Args:
            resume: Resume object
            jd: Job description
            style: Cover letter style
            why_interested: Optional personal interest statement
            company_research: Optional company research notes

        Returns:
            Dict with cover letter and metadata
        """
        print(f"\n{'='*60}")
        print(f"GENERATING COVER LETTER - {style.value.upper()} STYLE")
        print(f"{'='*60}")

        # Index resume and JD in RAG
        print("\nIndexing resume and JD for semantic matching...")
        self.rag_retriever.index_resume(resume)
        self.rag_retriever.index_job_description(jd)

        # Get top matching experiences using RAG
        print("Finding most relevant experiences...")
        matched_experiences = self._get_top_matching_experiences(resume, jd)

        # Get top matching skills
        print("Identifying key matching skills...")
        matched_skills = self._get_top_matching_skills(resume, jd)

        # Build JD summary
        jd_summary = self._build_jd_summary(jd)

        # Generate cover letter
        print(f"\nGenerating {style.value} cover letter...")
        prompt = self.prompts.get_cover_letter_prompt(
            candidate_name=resume.contact.full_name,
            job_title=jd.job_title,
            company=jd.company or "the company",
            job_description=jd_summary,
            matched_experiences=matched_experiences,
            key_skills=matched_skills,
            why_interested=why_interested,
            style=style
        )

        try:
            cover_letter = self.llm_service.generate(
                prompt,
                temperature=0.7,
                max_tokens=1000
            )

            print(f"✓ Cover letter generated successfully")

            return {
                'cover_letter': cover_letter.strip(),
                'style': style.value,
                'matched_experiences': matched_experiences,
                'matched_skills': matched_skills,
                'word_count': len(cover_letter.split()),
                'candidate_name': resume.contact.full_name,
                'job_title': jd.job_title,
                'company': jd.company
            }

        except Exception as e:
            print(f"⚠️  Error generating cover letter: {e}")
            return {
                'cover_letter': f"Error: {e}",
                'style': style.value,
                'matched_experiences': [],
                'matched_skills': [],
                'word_count': 0
            }

    def generate_multiple_styles(
        self,
        resume: Resume,
        jd: JobDescription,
        styles: List[CoverLetterStyle] = None
    ) -> Dict[str, Dict]:
        """
        Generate cover letters in multiple styles for comparison.

        Args:
            resume: Resume object
            jd: Job description
            styles: List of styles to generate (default: all)

        Returns:
            Dict mapping style names to cover letter results
        """
        if styles is None:
            styles = [
                CoverLetterStyle.PROFESSIONAL,
                CoverLetterStyle.ENTHUSIASTIC,
                CoverLetterStyle.CONCISE
            ]

        results = {}

        for style in styles:
            result = self.generate_cover_letter(resume, jd, style)
            results[style.value] = result

        print(f"\n{'='*60}")
        print(f"✓ Generated {len(results)} cover letter variations")
        print(f"{'='*60}")

        return results

    def generate_custom_sections(
        self,
        resume: Resume,
        jd: JobDescription,
        sections: Dict[str, str]
    ) -> Dict[str, str]:
        """
        Generate custom cover letter sections individually.

        Args:
            resume: Resume object
            jd: Job description
            sections: Dict of section names to prompts/requirements

        Returns:
            Dict of generated sections
        """
        generated_sections = {}

        # Opening paragraph
        if 'opening' in sections:
            print("\nGenerating opening paragraph...")
            opening_prompt = self.prompts.get_opening_paragraph_prompt(
                job_title=jd.job_title,
                company=jd.company or "the company",
                candidate_hook=sections.get('opening', ''),
                style=CoverLetterStyle.PROFESSIONAL
            )
            opening = self.llm_service.generate(opening_prompt, temperature=0.7, max_tokens=200)
            generated_sections['opening'] = opening.strip()

        # Experience highlights
        if 'experience' in sections:
            print("Generating experience highlights...")
            matched_experiences = self._get_top_matching_experiences(resume, jd)
            exp_prompt = self.prompts.get_experience_highlight_prompt(
                experiences=matched_experiences,
                job_requirements=jd.required_skills[:5],
                quantify=True
            )
            experience = self.llm_service.generate(exp_prompt, temperature=0.7, max_tokens=300)
            generated_sections['experience'] = experience.strip()

        # Why company
        if 'why_company' in sections:
            print("Generating 'why this company' paragraph...")
            company_research = sections.get('why_company', '')
            why_prompt = self.prompts.get_why_company_paragraph_prompt(
                company=jd.company or "the company",
                company_research=company_research,
                candidate_values="Innovation, growth, impact",
                style=CoverLetterStyle.PROFESSIONAL
            )
            why_company = self.llm_service.generate(why_prompt, temperature=0.7, max_tokens=200)
            generated_sections['why_company'] = why_company.strip()

        # Closing
        if 'closing' in sections:
            print("Generating closing paragraph...")
            closing_prompt = self.prompts.get_closing_paragraph_prompt(
                candidate_name=resume.contact.full_name,
                availability=sections.get('closing', 'immediately available'),
                style=CoverLetterStyle.PROFESSIONAL
            )
            closing = self.llm_service.generate(closing_prompt, temperature=0.7, max_tokens=150)
            generated_sections['closing'] = closing.strip()

        return generated_sections

    def _get_top_matching_experiences(
        self,
        resume: Resume,
        jd: JobDescription,
        top_k: int = 5
    ) -> List[str]:
        """Get top matching experience bullets using RAG."""
        matched_experiences = []

        # For each responsibility, find relevant experiences
        for responsibility in jd.responsibilities[:3]:  # Top 3 responsibilities
            relevant = self.rag_retriever.find_relevant_experiences_for_requirement(
                requirement=responsibility,
                top_k=2
            )

            for item in relevant:
                if item['similarity'] > 0.5:  # Threshold
                    matched_experiences.append(item['text'])

        # Deduplicate while preserving order
        seen = set()
        unique_experiences = []
        for exp in matched_experiences:
            if exp not in seen:
                seen.add(exp)
                unique_experiences.append(exp)

        return unique_experiences[:top_k]

    def _get_top_matching_skills(
        self,
        resume: Resume,
        jd: JobDescription,
        top_k: int = 10
    ) -> List[str]:
        """Get top matching skills between resume and JD."""
        # Get all experience text
        experience_text = " ".join([
            " ".join(exp.bullets) for exp in resume.experience
        ])

        # Match skills
        match_result = self.skill_matcher.match_skills(
            required_skills=jd.required_skills,
            resume_skills=resume.skills,
            experience_text=experience_text
        )

        # Extract matched skill names
        matched_skills = [
            match['required'] for match in match_result['matched_skills']
        ]

        return matched_skills[:top_k]

    def _build_jd_summary(self, jd: JobDescription, max_length: int = 800) -> str:
        """Build a concise summary of the job description."""
        summary = f"Job Title: {jd.job_title}\n"

        if jd.company:
            summary += f"Company: {jd.company}\n"

        if jd.overview:
            summary += f"\nOverview: {jd.overview}\n"

        if jd.responsibilities:
            summary += f"\nKey Responsibilities:\n"
            for resp in jd.responsibilities[:3]:
                summary += f"• {resp}\n"

        if jd.required_skills:
            summary += f"\nRequired Skills: {', '.join(jd.required_skills[:10])}\n"

        # Truncate if too long
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."

        return summary

    def save_cover_letter(
        self,
        cover_letter_result: Dict,
        output_path: str
    ):
        """
        Save cover letter to file.

        Args:
            cover_letter_result: Result dict from generate_cover_letter
            output_path: Output file path
        """
        with open(output_path, 'w') as f:
            f.write(cover_letter_result['cover_letter'])
            f.write("\n\n" + "="*60)
            f.write(f"\nSTYLE: {cover_letter_result['style']}")
            f.write(f"\nWORD COUNT: {cover_letter_result['word_count']}")
            f.write(f"\n\nKEY MATCHING SKILLS:")
            for skill in cover_letter_result['matched_skills'][:10]:
                f.write(f"\n• {skill}")

        print(f"✓ Cover letter saved to: {output_path}")
