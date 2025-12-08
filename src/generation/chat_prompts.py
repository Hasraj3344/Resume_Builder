"""Chat prompt templates for interactive Q&A about resumes."""

from typing import List, Dict, Optional


class ChatPromptTemplates:
    """Prompt templates for resume chat interface."""

    @staticmethod
    def get_resume_qa_prompt(
        question: str,
        retrieved_context: str,
        resume_summary: Optional[str] = None
    ) -> str:
        """
        Generate prompt for answering questions about resume.

        Args:
            question: User's question
            retrieved_context: Relevant resume sections from RAG
            resume_summary: Optional resume summary

        Returns:
            Formatted prompt
        """
        return f"""You are a helpful career advisor assistant helping a job seeker understand their resume.

USER QUESTION: {question}

RELEVANT RESUME INFORMATION:
{retrieved_context}

{"RESUME SUMMARY: " + resume_summary if resume_summary else ""}

INSTRUCTIONS:
1. Answer the question directly and concisely
2. Use specific details from the resume context provided
3. If the information isn't in the context, say you don't have that information
4. Be encouraging and professional
5. Provide actionable insights when relevant

Answer the user's question:"""

    @staticmethod
    def get_jd_match_prompt(
        question: str,
        resume_context: str,
        jd_context: str,
        match_score: Optional[float] = None
    ) -> str:
        """
        Generate prompt for JD matching questions.

        Args:
            question: User's question
            resume_context: Relevant resume sections
            jd_context: Relevant JD sections
            match_score: Overall match score

        Returns:
            Formatted prompt
        """
        return f"""You are a career advisor helping assess how well a resume matches a job description.

USER QUESTION: {question}

RESUME HIGHLIGHTS:
{resume_context}

JOB REQUIREMENTS:
{jd_context}

{"OVERALL MATCH SCORE: " + f"{match_score:.1%}" if match_score else ""}

INSTRUCTIONS:
1. Compare the resume against the job requirements
2. Highlight strengths and matching qualifications
3. Identify gaps or missing qualifications
4. Provide specific, actionable recommendations
5. Be honest but encouraging

Answer the user's question:"""

    @staticmethod
    def get_skill_query_prompt(
        skill: str,
        experience_context: str,
        skills_list: List[str]
    ) -> str:
        """
        Generate prompt for skill-specific questions.

        Args:
            skill: Skill being queried
            experience_context: Experience bullets mentioning the skill
            skills_list: All skills from resume

        Returns:
            Formatted prompt
        """
        has_skill = any(skill.lower() in s.lower() for s in skills_list)

        return f"""You are helping assess someone's experience with {skill}.

SKILL IN QUESTION: {skill}
LISTED IN SKILLS SECTION: {"Yes" if has_skill else "No"}

RELEVANT EXPERIENCE:
{experience_context if experience_context else "No specific experience found mentioning this skill."}

ALL SKILLS: {", ".join(skills_list[:20])}{"..." if len(skills_list) > 20 else ""}

INSTRUCTIONS:
1. Summarize their experience with {skill} based on the context
2. Mention specific projects or achievements if available
3. Assess their proficiency level if possible (beginner/intermediate/advanced)
4. If they don't have experience, suggest related skills they do have
5. Be honest and specific

Provide a comprehensive answer:"""

    @staticmethod
    def get_suggestion_prompt(
        current_state: str,
        missing_elements: List[str],
        context: str
    ) -> str:
        """
        Generate prompt for improvement suggestions.

        Args:
            current_state: Description of current resume state
            missing_elements: What's missing or could be improved
            context: Additional context

        Returns:
            Formatted prompt
        """
        return f"""You are a career coach providing actionable advice for resume improvement.

CURRENT SITUATION:
{current_state}

AREAS FOR IMPROVEMENT:
{chr(10).join(f"• {item}" for item in missing_elements)}

CONTEXT:
{context}

INSTRUCTIONS:
1. Provide 3-5 specific, actionable recommendations
2. Prioritize the most impactful improvements
3. Explain WHY each suggestion matters
4. Keep advice practical and achievable
5. Be encouraging and constructive

Provide your recommendations:"""

    @staticmethod
    def get_conversation_prompt(
        question: str,
        conversation_history: List[Dict[str, str]],
        current_context: str
    ) -> str:
        """
        Generate prompt with conversation history for follow-up questions.

        Args:
            question: Current question
            conversation_history: Previous Q&A pairs
            current_context: Retrieved context for current question

        Returns:
            Formatted prompt
        """
        history_text = ""
        if conversation_history:
            history_text = "PREVIOUS CONVERSATION:\n"
            for item in conversation_history[-3:]:  # Last 3 exchanges
                history_text += f"User: {item['question']}\n"
                history_text += f"Assistant: {item['answer']}\n\n"

        return f"""You are a career advisor having a conversation about someone's resume and job search.

{history_text}
CURRENT QUESTION: {question}

RELEVANT INFORMATION:
{current_context}

INSTRUCTIONS:
1. Consider the conversation context
2. Answer the current question directly
3. Reference previous discussion if relevant
4. Provide specific, helpful information
5. Be conversational and professional

Answer the question:"""

    @staticmethod
    def classify_question_type(question: str) -> str:
        """
        Classify the type of question being asked.

        Args:
            question: User's question

        Returns:
            Question type: 'skill', 'experience', 'match', 'suggestion', 'general'
        """
        question_lower = question.lower()

        # Skill queries
        if any(phrase in question_lower for phrase in [
            'do i know', 'do i have experience with', 'am i familiar with',
            'what is my experience with', 'how much do i know about'
        ]):
            return 'skill'

        # Experience queries
        if any(phrase in question_lower for phrase in [
            'what experience', 'have i worked', 'have i used',
            'what projects', 'where did i', 'when did i'
        ]):
            return 'experience'

        # Match queries
        if any(phrase in question_lower for phrase in [
            'how well do i match', 'do i qualify', 'am i a good fit',
            'match score', 'meet the requirements', 'qualified for'
        ]):
            return 'match'

        # Suggestion queries
        if any(phrase in question_lower for phrase in [
            'what should i add', 'how can i improve', 'what am i missing',
            'what skills should', 'how to strengthen', 'recommendations'
        ]):
            return 'suggestion'

        # Default to general
        return 'general'
