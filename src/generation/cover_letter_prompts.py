"""Prompt templates for cover letter generation."""

from typing import List, Dict, Optional
from enum import Enum


class CoverLetterStyle(Enum):
    """Cover letter style options."""
    FORMAL = "formal"
    PROFESSIONAL = "professional"
    ENTHUSIASTIC = "enthusiastic"
    STORYTELLING = "storytelling"
    CONCISE = "concise"


class CoverLetterPrompts:
    """Prompt templates for generating cover letters."""

    @staticmethod
    def get_cover_letter_prompt(
        candidate_name: str,
        job_title: str,
        company: str,
        job_description: str,
        matched_experiences: List[str],
        key_skills: List[str],
        why_interested: str = None,
        style: CoverLetterStyle = CoverLetterStyle.PROFESSIONAL
    ) -> str:
        """
        Generate a complete cover letter based on resume-JD matching.

        Args:
            candidate_name: Candidate's name
            job_title: Target job title
            company: Company name
            job_description: Full or summarized JD
            matched_experiences: Top matching experience bullets from RAG
            key_skills: Top matching skills
            why_interested: Optional personal interest in role/company
            style: Cover letter style

        Returns:
            Formatted prompt string
        """
        experiences_text = "\n".join([f"• {exp}" for exp in matched_experiences[:5]])
        skills_text = ", ".join(key_skills[:10])

        style_guidance = CoverLetterPrompts._get_style_guidance(style)

        interest_section = f"""
CANDIDATE'S INTEREST IN ROLE/COMPANY:
{why_interested}
""" if why_interested else ""

        prompt = f"""You are a professional cover letter writer specializing in creating compelling, personalized cover letters.

CANDIDATE INFORMATION:
Name: {candidate_name}

TARGET POSITION:
Job Title: {job_title}
Company: {company}

JOB DESCRIPTION (KEY POINTS):
{job_description[:800]}...

TOP MATCHING EXPERIENCES (from resume):
{experiences_text}

KEY MATCHING SKILLS:
{skills_text}
{interest_section}

STYLE GUIDANCE:
{style_guidance}

YOUR TASK:
Write a compelling cover letter that:
1. Opens with a strong hook that shows genuine interest in the role
2. Demonstrates clear understanding of the company's needs
3. Highlights 2-3 most relevant experiences from the matched list
4. Shows how candidate's skills directly address job requirements
5. Conveys personality and cultural fit
6. Ends with a confident call to action

STRUCTURE (4 paragraphs):
1. **Opening** (2-3 sentences): Hook + express interest + mention how you learned about role
2. **Why You're a Great Fit** (4-5 sentences): Highlight 2-3 relevant experiences with specific achievements
3. **Why This Company/Role** (3-4 sentences): Show research, alignment with company mission, enthusiasm
4. **Closing** (2-3 sentences): Call to action, availability, professional closing

REQUIREMENTS:
• Keep total length to 300-400 words (read time: 1-2 minutes)
• Be specific - use real details from experiences provided
• Avoid clichés like "I am writing to apply..." or "I am the perfect candidate"
• Sound authentic and conversational, not robotic
• Show enthusiasm without being overeager
• Proofread for grammar and flow

OUTPUT FORMAT:
Dear Hiring Manager,

[Opening paragraph]

[Body paragraph 1 - Your fit]

[Body paragraph 2 - Why this company]

[Closing paragraph]

Sincerely,
{candidate_name}

COVER LETTER:"""

        return prompt

    @staticmethod
    def _get_style_guidance(style: CoverLetterStyle) -> str:
        """Get style-specific writing guidance."""

        if style == CoverLetterStyle.FORMAL:
            return """• Use formal business language and traditional structure
• Maintain professional distance and respectful tone
• Avoid contractions (use "I am" not "I'm")
• Focus on qualifications and credentials
• Use traditional phrases like "I am pleased to submit..." """

        elif style == CoverLetterStyle.PROFESSIONAL:
            return """• Use clear, professional language with some warmth
• Balance professionalism with personality
• Use active voice and confident statements
• Focus on value proposition and impact
• Demonstrate both competence and culture fit"""

        elif style == CoverLetterStyle.ENTHUSIASTIC:
            return """• Show genuine excitement about the opportunity
• Use energetic language while remaining professional
• Express passion for the company's mission/products
• Emphasize eagerness to contribute
• Let personality shine through while staying credible"""

        elif style == CoverLetterStyle.STORYTELLING:
            return """• Open with a brief, relevant story or anecdote
• Use narrative elements to engage reader
• Show how past experiences led to this opportunity
• Create emotional connection through authentic voice
• Still hit key qualifications but in a story format"""

        elif style == CoverLetterStyle.CONCISE:
            return """• Keep extremely brief (250-300 words max)
• Use bullet points for key qualifications if needed
• Every sentence must add value
• Remove filler words and phrases
• Get straight to the point - busy readers will appreciate"""

        return ""  # Default

    @staticmethod
    def get_opening_paragraph_prompt(
        job_title: str,
        company: str,
        candidate_hook: str,
        style: CoverLetterStyle = CoverLetterStyle.PROFESSIONAL
    ) -> str:
        """
        Generate just the opening paragraph.

        Args:
            job_title: Target job title
            company: Company name
            candidate_hook: Unique hook about candidate
            style: Writing style

        Returns:
            Formatted prompt
        """
        style_guidance = CoverLetterPrompts._get_style_guidance(style)

        prompt = f"""You are writing the opening paragraph of a cover letter.

TARGET POSITION:
{job_title} at {company}

CANDIDATE HOOK:
{candidate_hook}

STYLE:
{style_guidance}

YOUR TASK:
Write a compelling 2-3 sentence opening paragraph that:
1. Immediately captures attention with a strong hook
2. Clearly states the position you're applying for
3. Gives a preview of why you're an excellent fit

AVOID:
• "I am writing to apply for..."
• Generic statements that could apply to anyone
• Starting with your name

GOOD EXAMPLES:
• "When I read about {company}'s initiative on [X], I immediately saw how my 5 years building scalable data pipelines aligns with your mission..."
• "Turning raw data into actionable insights has been my passion for the past 4 years, which is why the {job_title} position at {company} feels like the perfect next step..."

Write only the opening paragraph:"""

        return prompt

    @staticmethod
    def get_why_company_paragraph_prompt(
        company: str,
        company_research: str,
        candidate_values: str,
        style: CoverLetterStyle = CoverLetterStyle.PROFESSIONAL
    ) -> str:
        """
        Generate the "why this company" paragraph.

        Args:
            company: Company name
            company_research: Research about company (mission, products, culture)
            candidate_values: What candidate values/seeks in a company
            style: Writing style

        Returns:
            Formatted prompt
        """
        style_guidance = CoverLetterPrompts._get_style_guidance(style)

        prompt = f"""You are writing the "why this company" paragraph of a cover letter.

COMPANY:
{company}

COMPANY RESEARCH:
{company_research}

CANDIDATE VALUES:
{candidate_values}

STYLE:
{style_guidance}

YOUR TASK:
Write a compelling 3-4 sentence paragraph that:
1. Shows you've researched the company
2. Connects company's mission/values to your own
3. Expresses genuine enthusiasm for the opportunity
4. Mentions specific aspects that excite you (products, culture, impact, growth)

REQUIREMENTS:
• Be specific - mention actual company initiatives, products, or values
• Sound authentic, not like generic flattery
• Show how joining would benefit both parties

Write only this paragraph:"""

        return prompt

    @staticmethod
    def get_experience_highlight_prompt(
        experiences: List[str],
        job_requirements: List[str],
        quantify: bool = True
    ) -> str:
        """
        Generate experience highlights for the body paragraph.

        Args:
            experiences: Candidate's relevant experiences
            job_requirements: Key requirements from JD
            quantify: Whether to emphasize metrics

        Returns:
            Formatted prompt
        """
        exp_text = "\n".join([f"• {exp}" for exp in experiences[:5]])
        req_text = "\n".join([f"• {req}" for req in job_requirements[:5]])

        quantify_note = """
IMPORTANT: Emphasize quantifiable achievements:
• Use percentages, numbers, scale (e.g., "reduced processing time by 40%", "managed $2M budget")
• Include scope (e.g., "across 50+ projects", "serving 10,000+ users")
• Show before/after improvements where possible""" if quantify else ""

        prompt = f"""You are writing the experience highlight section of a cover letter.

CANDIDATE'S RELEVANT EXPERIENCES:
{exp_text}

JOB REQUIREMENTS:
{req_text}
{quantify_note}

YOUR TASK:
Write 4-5 sentences highlighting the 2-3 most relevant experiences that directly address the job requirements.

REQUIREMENTS:
• Choose experiences that best match the job requirements
• Be specific about what you did and the impact
• Use strong action verbs (Led, Architected, Optimized, etc.)
• Connect each experience to a job requirement
• Flow naturally - not just a list

EXAMPLE:
"In my current role as Data Engineer at TechCorp, I architected scalable data pipelines processing 5TB+ daily, reducing processing time by 45% through optimization strategies that directly align with your need for high-performance systems. I also led the migration of legacy ETL workflows to cloud-native solutions, improving reliability by 60% and cutting costs by $200K annually..."

Write the experience highlight section:"""

        return prompt

    @staticmethod
    def get_closing_paragraph_prompt(
        candidate_name: str,
        availability: str = "immediately available",
        style: CoverLetterStyle = CoverLetterStyle.PROFESSIONAL
    ) -> str:
        """
        Generate closing paragraph.

        Args:
            candidate_name: Candidate's name
            availability: Availability statement
            style: Writing style

        Returns:
            Formatted prompt
        """
        style_guidance = CoverLetterPrompts._get_style_guidance(style)

        prompt = f"""You are writing the closing paragraph of a cover letter.

CANDIDATE:
{candidate_name}

AVAILABILITY:
{availability}

STYLE:
{style_guidance}

YOUR TASK:
Write a strong 2-3 sentence closing paragraph that:
1. Reiterates interest and fit
2. Includes a clear call to action
3. Mentions availability if relevant
4. Ends confidently and professionally

REQUIREMENTS:
• Be confident but not presumptuous
• Invite next steps (interview, conversation)
• Thank them appropriately
• End with "Sincerely," or "Best regards,"

AVOID:
• "I look forward to hearing from you" (too passive)
• "Please feel free to contact me" (too formal)
• Apologetic language

GOOD EXAMPLES:
• "I'm excited about the opportunity to bring my data engineering expertise to [Company] and would welcome the chance to discuss how I can contribute to your team's success. I'm available for an interview at your convenience."
• "I'm confident that my experience in [X] and passion for [Y] make me an excellent fit for this role. Let's schedule a time to discuss how I can add value to your team."

Write only the closing paragraph and sign-off:"""

        return prompt
