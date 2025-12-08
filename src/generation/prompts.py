"""Prompt templates for LLM-based resume optimization."""

from typing import List, Dict


class PromptTemplates:
    """Collection of prompt templates for resume generation."""

    @staticmethod
    def get_bullet_rewrite_prompt(
        original_bullet: str,
        jd_requirement: str,
        missing_keywords: List[str],
        context: Dict = None
    ) -> str:
        """
        Generate prompt for rewriting a single experience bullet.

        Args:
            original_bullet: Original resume bullet point
            jd_requirement: Relevant job description requirement
            missing_keywords: Keywords to naturally incorporate
            context: Additional context (company, title, etc.)

        Returns:
            Formatted prompt string
        """
        keywords_str = ", ".join(missing_keywords) if missing_keywords else "none"

        prompt = f"""You are an expert resume writer specializing in ATS optimization and the STAR method (Situation, Task, Action, Result).

Your task is to rewrite the following resume bullet point to better match the job requirement while maintaining authenticity and impact.

ORIGINAL BULLET:
{original_bullet}

JOB REQUIREMENT TO MATCH:
{jd_requirement}

KEYWORDS TO INCORPORATE (naturally):
{keywords_str}

GUIDELINES:
1. Use the STAR method structure (Situation/Task → Action → Result)
2. Start with a strong action verb (Led, Architected, Optimized, Implemented, etc.)
3. Naturally incorporate the missing keywords where relevant
4. Quantify results with specific metrics when possible (%, numbers, time saved)
5. Match the terminology and tone of the job description
6. Keep it concise (1-2 lines, maximum 150 words)
7. Focus on impact and outcomes
8. Maintain truthfulness - don't fabricate achievements

OUTPUT FORMAT:
Return only the rewritten bullet point, nothing else. Start with a bullet symbol (•).

REWRITTEN BULLET:"""

        return prompt

    @staticmethod
    def get_multi_bullet_optimization_prompt(
        original_bullets: List[str],
        jd_responsibilities: List[str],
        missing_keywords: List[str],
        company: str = "",
        title: str = ""
    ) -> str:
        """
        Generate prompt for optimizing multiple bullets together.

        Args:
            original_bullets: List of original bullet points
            jd_responsibilities: Key responsibilities from JD
            missing_keywords: Keywords to incorporate
            company: Company name
            title: Job title

        Returns:
            Formatted prompt string
        """
        bullets_text = "\n".join([f"{i+1}. {b}" for i, b in enumerate(original_bullets)])
        resp_text = "\n".join([f"• {r}" for r in jd_responsibilities[:5]])
        keywords_text = ", ".join(missing_keywords[:10])

        prompt = f"""You are an expert resume writer specializing in ATS optimization.

CONTEXT:
Position: {title} at {company}

ORIGINAL EXPERIENCE BULLETS:
{bullets_text}

KEY JOB RESPONSIBILITIES TO ALIGN WITH:
{resp_text}

MISSING KEYWORDS TO INCORPORATE:
{keywords_text}

YOUR TASK:
Rewrite and optimize these experience bullets to maximize relevance for this role.

REQUIREMENTS:
1. Rewrite each bullet using the STAR method (Situation/Task → Action → Result)
2. Start each bullet with strong action verbs (Architected, Spearheaded, Optimized, etc.)
3. Naturally incorporate missing keywords where they fit authentically
4. Quantify achievements with specific metrics (%, $, time saved, scale)
5. Emphasize technologies and skills mentioned in the job responsibilities
6. Keep each bullet to 1-2 lines (max 150 words)
7. Maintain authenticity - don't fabricate achievements
8. Order bullets by relevance to the job requirements (most relevant first)

OUTPUT FORMAT:
Return 5-7 rewritten bullets in this exact format:
• [Bullet point 1]
• [Bullet point 2]
...

OPTIMIZED BULLETS:"""

        return prompt

    @staticmethod
    def get_summary_optimization_prompt(
        original_summary: str,
        jd_overview: str,
        job_title: str,
        key_skills: List[str],
        years_experience: str = ""
    ) -> str:
        """
        Generate prompt for optimizing professional summary.

        Args:
            original_summary: Original summary text
            jd_overview: Job description overview
            job_title: Target job title
            key_skills: Most important skills to highlight
            years_experience: Years of experience required

        Returns:
            Formatted prompt string
        """
        skills_text = ", ".join(key_skills[:8])

        years_instruction = ""
        if years_experience:
            years_instruction = f"""
CRITICAL REQUIREMENT - YEARS OF EXPERIENCE:
You MUST include exactly "{years_experience} years of experience" in the opening sentence.
Example: "{job_title} with {years_experience} years of experience in..."
DO NOT change or omit the years. Use the exact value provided: {years_experience}
"""

        prompt = f"""You are an expert resume writer specializing in compelling professional summaries.

TARGET ROLE:
{job_title}

JOB OVERVIEW:
{jd_overview}

ORIGINAL SUMMARY:
{original_summary}

KEY SKILLS TO HIGHLIGHT:
{skills_text}
{years_instruction}
YOUR TASK:
Rewrite the professional summary to perfectly align with this specific role.

REQUIREMENTS:
1. Open with a strong professional title/identity including years of experience
2. Highlight the 5-7 most relevant skills and technologies
3. Match the language and terminology from the job description
4. Keep it concise: 3-4 sentences (60-80 words)
5. Focus on value proposition and key strengths
6. Use industry-standard terminology
7. Make it ATS-friendly (keyword-rich but natural)

OUTPUT FORMAT:
Return only the rewritten summary, no additional text.

OPTIMIZED SUMMARY:"""

        return prompt

    @staticmethod
    def get_achievement_enhancement_prompt(
        bullet: str,
        add_metrics: bool = True
    ) -> str:
        """
        Generate prompt for enhancing a bullet with stronger impact.

        Args:
            bullet: Original bullet point
            add_metrics: Whether to suggest adding metrics

        Returns:
            Formatted prompt string
        """
        metrics_instruction = """
- Add specific metrics where possible (%, numbers, scale, time)
- If exact numbers aren't available, use realistic ranges or approximations""" if add_metrics else ""

        prompt = f"""You are an expert at transforming weak resume bullets into high-impact achievement statements.

ORIGINAL BULLET:
{bullet}

YOUR TASK:
Transform this into a powerful achievement statement that demonstrates clear impact and value.

REQUIREMENTS:
1. Use the STAR method structure (Situation → Action → Result)
2. Start with a powerful action verb
3. Focus on the RESULT and IMPACT{metrics_instruction}
4. Make it specific and concrete
5. Keep it concise (1-2 lines)
6. Maintain authenticity

EXAMPLES OF GOOD TRANSFORMATIONS:
Before: "Worked on data pipelines"
After: "Architected and deployed 15+ production data pipelines processing 2TB+ daily data, reducing processing time by 40%"

Before: "Improved system performance"
After: "Optimized database queries and implemented caching strategies, improving API response time by 65% (from 800ms to 280ms)"

OUTPUT FORMAT:
Return only the enhanced bullet point.

ENHANCED BULLET:"""

        return prompt

    @staticmethod
    def get_keyword_injection_prompt(
        bullet: str,
        keywords: List[str]
    ) -> str:
        """
        Generate prompt for naturally injecting keywords into a bullet.

        Args:
            bullet: Original bullet point
            keywords: Keywords to inject

        Returns:
            Formatted prompt string
        """
        keywords_text = ", ".join(keywords)

        prompt = f"""You are an expert at naturally incorporating keywords into resume bullets for ATS optimization.

ORIGINAL BULLET:
{bullet}

KEYWORDS TO INCORPORATE:
{keywords_text}

YOUR TASK:
Rewrite this bullet to naturally include as many of these keywords as possible WITHOUT making it sound forced or keyword-stuffed.

REQUIREMENTS:
1. Maintain the core meaning and achievement
2. Only add keywords that fit naturally and authentically
3. Keep the bullet professional and readable
4. Don't sacrifice clarity for keyword density
5. Keep it concise (1-2 lines)

OUTPUT FORMAT:
Return only the rewritten bullet.

OPTIMIZED BULLET:"""

        return prompt

    @staticmethod
    def get_skills_optimization_prompt(
        current_skills: List[str],
        jd_required_skills: List[str],
        jd_preferred_skills: List[str]
    ) -> str:
        """
        Generate prompt for optimizing skills section.

        Args:
            current_skills: Current skills list
            jd_required_skills: Required skills from JD
            jd_preferred_skills: Preferred skills from JD

        Returns:
            Formatted prompt string
        """
        current_text = ", ".join(current_skills)
        required_text = ", ".join(jd_required_skills)
        preferred_text = ", ".join(jd_preferred_skills)

        prompt = f"""You are an expert at optimizing resume skills sections for ATS and recruiter appeal.

CURRENT SKILLS:
{current_text}

JOB REQUIRED SKILLS:
{required_text}

JOB PREFERRED SKILLS:
{preferred_text}

YOUR TASK:
Reorganize and optimize the skills section to maximize relevance for this job.

REQUIREMENTS:
1. Prioritize required skills from the job description at the top
2. Group related skills together
3. Use exact terminology from the job description where possible
4. Include skill variations (e.g., "Python (PySpark)" instead of just "Python")
5. Remove skills irrelevant to this role
6. Add skill categories if it improves organization
7. Keep it ATS-friendly (comma-separated or categorized)

OUTPUT FORMAT:
Return the optimized skills list in this format:
Category: skill1, skill2, skill3
Category: skill1, skill2, skill3

Or if no categories needed:
skill1, skill2, skill3, skill4...

OPTIMIZED SKILLS:"""

        return prompt

    @staticmethod
    def get_enhanced_professional_summary_prompt(
        experience_text: str,
        job_description: str,
        years_of_experience: str,
        job_title: str = "Data Engineer"
    ) -> str:
        """
        Generate enhanced professional summary with WHR format (20-25 bullets).
        Based on sample_prompts.md specifications.

        Args:
            experience_text: Candidate's professional experience
            job_description: Full job description text
            years_of_experience: Years of experience (e.g., "5+")
            job_title: Target job title

        Returns:
            Formatted prompt string
        """
        prompt = f"""You are a Resume Summary & Skills Assistant.
Your task is to generate a Professional Summary based on the candidate's professional experience and the provided job description.

CORE RULES FOR PROFESSIONAL SUMMARY:

Opening Line Rule:
• Always start the first bullet as: "{job_title} with {years_of_experience} years of experience, including [modules/areas from the JD]."

Structure & Quantity:
• Generate 20–25 bullet points
• Each bullet must be 20–30 words
• Each statement must follow the WHR Format → (What – How – Result)
• Do not use symbols such as "•", "–", or "➤" at the beginning
• Maintain exactly one space gap between bullets

Content Focus:
• Include relevant domain expertise (e.g. Databricks, Azure Fabric, AI/ML, etc. as per the job description)
• Add consulting/project management elements (onsite–offshore coordination, client interaction, stakeholder management)
• Incorporate measurable outcomes (improved efficiency, reduced downtime, automated processes, enhanced compliance)
• Use ATS keywords directly from the JD to enhance visibility
• Highlight all important keywords in **bold** (e.g., **DataBricks**, **Pipeline Development**, **Cloud AWS/Azure**)

Stylistic Guidelines:
• Maintain a crisp, professional, and keyword-rich tone
• Ensure consistency in formatting, tense, and structure
• Avoid repetition and filler phrases
• Focus on impact and quantifiable contributions

CANDIDATE'S PROFESSIONAL EXPERIENCE:
{experience_text}

JOB DESCRIPTION:
{job_description}

OUTPUT FORMAT:
Generate 20-25 professional summary bullet points following the WHR format. Start each bullet point on a new line without bullet symbols. Bold the important keywords using **keyword** format.

PROFESSIONAL SUMMARY:"""

        return prompt

    @staticmethod
    def get_technical_skills_table_prompt(
        current_skills: List[str],
        jd_text: str
    ) -> str:
        """
        Generate technical skills organized in a table format by category.
        Based on sample_prompts.md specifications.

        Args:
            current_skills: List of current skills from resume
            jd_text: Job description text

        Returns:
            Formatted prompt string
        """
        skills_text = ", ".join(current_skills)

        prompt = f"""You are a Resume Technical Skills Organizer.
Your task is to generate a Technical Skills Table based on the candidate's skills and the job description.

CORE RULES FOR TECHNICAL SKILLS TABLE:

Presentation Format:
• Display in a clean, structured table grouped by categories:
  - Cloud Platforms (Azure, AWS, GCP)
  - Big Data & Processing (Databricks, Spark, PySpark, Kafka)
  - Databases (SQL Server, PostgreSQL, MongoDB, Snowflake, Delta Lake)
  - Data Engineering Tools (Azure Data Factory, Airflow, SSIS, ETL/ELT)
  - Programming Languages (Python, SQL, Scala, Java)
  - DevOps & CI/CD (Git, Docker, Kubernetes, Jenkins, Azure DevOps)
  - Analytics & BI (Power BI, Tableau, Looker)
  - Other Tools & Frameworks

Content Guidelines:
• Include only relevant technologies aligned to the job description
• Use ATS-friendly, concise phrasing
• Maintain consistent formatting and capitalization
• List technologies in order of relevance

Style:
• Ensure readability and scanning ease
• Keep it clean, modern, and keyword-rich
• Highlight cross-module expertise and domain specialization

CANDIDATE'S CURRENT SKILLS:
{skills_text}

JOB DESCRIPTION:
{jd_text}

OUTPUT FORMAT:
Generate a categorized technical skills table. Use this format:

**Category Name**
skill1, skill2, skill3, skill4

**Category Name**
skill1, skill2, skill3

TECHNICAL SKILLS TABLE:"""

        return prompt

    @staticmethod
    def get_client_environment_prompt(
        company: str,
        location: str,
        start_date: str,
        end_date: str,
        is_current: bool,
        original_bullets: List[str],
        job_description: str,
        is_fresher_role: bool = False
    ) -> str:
        """
        Generate client/project section with environment details.
        Based on sample_prompts.md specifications.

        Args:
            company: Client/company name
            location: Location
            start_date: Start date
            end_date: End date
            is_current: Whether this is the current role
            original_bullets: Original experience bullets
            job_description: Job description text
            is_fresher_role: Special handling for fresher/entry-level roles

        Returns:
            Formatted prompt string
        """
        bullets_text = "\n".join([f"{i+1}. {b}" for i, b in enumerate(original_bullets)])
        verb_tense = "present tense" if is_current else "past tense"

        bullet_count = "10–15" if is_fresher_role else "20–25"
        verb_guidance = """
SPECIAL RULE — FRESHER/ENTRY-LEVEL CLIENT:
• Reflect entry-level exposure — avoid leadership verbs
• Focus areas: Learning, Assisting, Documentation, Testing, Basic Configuration, End-User Support
• Use beginner verbs only: Assisted, Supported, Participated, Involved in, Worked on, Learned
• Keep tasks realistic — emphasize supporting senior team members, handling documentation/testing""" if is_fresher_role else """
SENIOR-LEVEL GUIDELINES:
• Use leadership and ownership verbs: Led, Architected, Spearheaded, Drove, Established, Designed
• Highlight achievements and measurable results
• Show technical depth and business impact"""

        prompt = f"""You are a Resume Project Experience Writer.
Your task is to generate a detailed client/project experience section based on the candidate's work and job description.

GENERAL RULES:
• Include quantifiable outcomes wherever possible (e.g., Reduced processing time by 20%, Supported 50+ users)
• Always align bullet points with keywords from the Job Description
• Make keywords, client names, and technologies **bold**
• Generate {bullet_count} detailed bullet points
• Avoid short one-liners; maintain mid-length, detailed, yet concise statements
• Avoid duplication or repetition
• Maintain professional tone and ATS-optimized phrasing
• Use **{verb_tense}** for all bullets

{verb_guidance}

ENVIRONMENT SECTION RULES:
• Provide Environment tools and technologies based on the Job Description
• Environment section must be a minimum of 3 lines long
• Include relevant technologies mentioned in JD
• Format: Environment: Tool1, Tool2, Tool3, ...

FORMATTING RULES:
• No bullet symbols (like •, ➤, –) at the start
• Use plain bullet format with one space gap after each bullet
• Do not bold entire sentences — only keywords, client names, and technologies
• Ensure Word-ready formatting

STYLE & WRITING GUIDELINES:
• Use professional, concise, and ATS-friendly tone
• Highlight achievements and measurable results
• Maintain logical flow: Requirement → Action → Result
• Keep focus on technical implementation, integration, testing, and support

CLIENT/PROJECT DETAILS:
Company: {company}
Location: {location}
Duration: {start_date} – {end_date}

ORIGINAL EXPERIENCE BULLETS:
{bullets_text}

JOB DESCRIPTION:
{job_description}

OUTPUT FORMAT:
First, provide the Environment section (3+ lines), then provide {bullet_count} bullet points without bullet symbols.

ENVIRONMENT:

CLIENT EXPERIENCE BULLETS:"""

        return prompt

    @staticmethod
    def get_ats_score_prompt(
        resume_text: str,
        job_description: str
    ) -> str:
        """
        Generate ATS score analysis for resume vs job description.
        Based on sample_prompts.md specifications.

        Args:
            resume_text: Full resume text
            job_description: Job description text

        Returns:
            Formatted prompt string
        """
        prompt = f"""You are an ATS (Applicant Tracking System) Resume Analyzer.
Your task is to analyze how well a resume matches a job description and provide a detailed ATS score.

SCORING METHOD:

1. Keyword Match (40%): Extract important keywords/skills from JD and check if they appear in resume
2. Experience Match (30%): Compare years, tools, and role responsibilities
3. Format & Readability (10%): ATS-friendly formatting (no tables, graphics, fancy fonts)
4. Relevance & Action Verbs (20%): Strong bullet points with measurable impact, alignment with role

OUTPUT FORMAT:

**Overall ATS Score**: X/100

**Breakdown by Category:**
• Keyword Match: X/40
• Experience Match: X/30
• Format & Readability: X/10
• Relevance & Action Verbs: X/20

**Missing Keywords** (what's missing from resume vs JD):
• **keyword1**
• **keyword2**
• **keyword3**

**Strengths** (what is well covered):
• strength1
• strength2
• strength3

**Recommendations** (specific, actionable improvements):
1. recommendation1
2. recommendation2
3. recommendation3

**Tone & Style:**
• Be objective and concise
• Use bullet points for recommendations
• Highlight keywords in **bold** so user can copy easily

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}

ATS ANALYSIS:"""

        return prompt

    @staticmethod
    def get_email_application_prompt(
        job_title: str,
        company: str,
        job_description: str,
        candidate_name: str,
        key_qualifications: List[str]
    ) -> str:
        """
        Generate email subject and body for job application.
        Based on sample_prompts.md specifications.

        Args:
            job_title: Target job title
            company: Company name
            job_description: Job description text
            candidate_name: Candidate's name
            key_qualifications: Top 3-5 qualifications

        Returns:
            Formatted prompt string
        """
        quals_text = "\n".join([f"• {q}" for q in key_qualifications[:5]])

        prompt = f"""You are a Professional Email Writer for job applications.
Your task is to generate an email subject and description for applying to a position.

CONTEXT:
Position: {job_title}
Company: {company}
Candidate: {candidate_name}

KEY QUALIFICATIONS:
{quals_text}

JOB DESCRIPTION:
{job_description}

REQUIREMENTS:
• Create a compelling subject line (concise, professional)
• Write a brief email body (3-4 paragraphs)
• Highlight key qualifications that match the JD
• Express enthusiasm for the role
• Include a clear call to action
• Maintain professional yet personable tone
• Keep total length under 200 words

OUTPUT FORMAT:
**Subject:** [subject line]

**Email Body:**
[email content]

EMAIL FOR JOB APPLICATION:"""

        return prompt
